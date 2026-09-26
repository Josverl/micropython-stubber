"""Cross-file inheritance metadata for doc-stub enrichment."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Dict, Mapping, Optional, Sequence, Tuple

import libcst as cst

from stubber.typing_collector import AnnoValue, StubTypingCollector

_code = cst.parse_module("").code_for_node
_INSPECT_PLACEHOLDER = re.compile(r"(?:(?:self|cls), )?x\d+(?:, x\d+)*")
_UNKNOWN_PARAMETERS = {
    "",
    "...",
    "*args, **kwargs",
    "self",
    "self, *args, **kwargs",
    "cls",
    "cls, *args, **kwargs",
}
_WEAK_RETURNS = {"...", "Any", "Incomplete"}


@dataclass(frozen=True, order=True)
class ClassId:
    """A class identity qualified by its final target module."""

    module: str
    qualname: Tuple[str, ...]

    @property
    def display_name(self) -> str:
        return ".".join((self.module, *self.qualname))


@dataclass(frozen=True)
class MethodSummary:
    """The immutable method facts needed for a pruning decision."""

    is_richer_than_placeholder: bool
    arities: Optional[frozenset[int]]
    fingerprint: str


@dataclass(frozen=True)
class ClassSummary:
    """Documented bases and methods for one class."""

    class_id: ClassId
    bases: Tuple[ClassId, ...]
    methods: Mapping[str, MethodSummary]


@dataclass(frozen=True)
class InheritanceSource:
    """A doc-stub source and the final module it enriches."""

    path: Path
    source_module: str
    target_module: str


@dataclass
class _ClassBuilder:
    bases: Tuple[ClassId, ...] = ()
    methods: Dict[str, MethodSummary] = field(default_factory=dict)


class InheritanceIndex:
    """Read-only class metadata shared by an enrichment run."""

    def __init__(self, classes: Optional[Mapping[ClassId, ClassSummary]] = None) -> None:
        self._classes = MappingProxyType(dict(classes or {}))

    def resolve_method(self, child: ClassId, method_name: str) -> Optional[Tuple[ClassId, MethodSummary]]:
        """Resolve a method through an unambiguous single-inheritance chain."""
        child = ClassId(_normalize_module(child.module), child.qualname)
        summary = self._classes.get(child)
        if summary is None or len(summary.bases) != 1:
            return None

        current = summary.bases[0]
        visited = {child}
        while current not in visited:
            visited.add(current)
            parent = self._classes.get(current)
            if parent is None:
                return None
            if method := parent.methods.get(method_name):
                return current, method
            if len(parent.bases) != 1:
                return None
            current = parent.bases[0]
        return None

    def fingerprint_for_module(self, module: str) -> str:
        """Hash classes in a module and their indexed ancestor dependencies."""
        pending = [class_id for class_id in self._classes if class_id.module == _normalize_module(module)]
        included = set()
        while pending:
            class_id = pending.pop()
            if class_id in included:
                continue
            included.add(class_id)
            if summary := self._classes.get(class_id):
                pending.extend(summary.bases)

        lines = []
        for class_id in sorted(included):
            summary = self._classes.get(class_id)
            if summary is None:
                lines.append(f"missing:{class_id.display_name}")
                continue
            lines.append(f"class:{class_id.display_name}")
            lines.extend(f"base:{base.display_name}" for base in summary.bases)
            lines.extend(f"method:{name}:{method.fingerprint}" for name, method in sorted(summary.methods.items()))
        return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def build_inheritance_index(sources: Sequence[InheritanceSource]) -> InheritanceIndex:
    """Build module-qualified inheritance metadata from doc-stub sources."""
    module_aliases = {_normalize_module(source.source_module): _normalize_module(source.target_module) for source in sources}
    builders: Dict[ClassId, _ClassBuilder] = {}

    for source in sorted(sources, key=lambda item: item.path.as_posix()):
        tree = cst.parse_module(source.path.read_text(encoding="utf-8"))
        collector = StubTypingCollector()
        tree.visit(collector)
        imports = _ImportCollector(source, module_aliases)
        tree.visit(imports)
        target_module = _normalize_module(source.target_module)

        for class_key, annotation in collector.annotations.items():
            if annotation.type_info is None or not isinstance(annotation.type_info.def_node, cst.ClassDef):
                continue
            class_id = ClassId(target_module, class_key)
            class_node = annotation.type_info.def_node
            bases = tuple(base_id for base in class_node.bases if (base_id := imports.resolve_base(base.value, class_id)) is not None)
            builder = builders.setdefault(class_id, _ClassBuilder())
            if bases:
                builder.bases = bases

            for method_key, method_annotation in collector.annotations.items():
                if len(method_key) != len(class_key) + 1 or method_key[:-1] != class_key:
                    continue
                if summary := _summarize_method(method_annotation):
                    builder.methods[method_key[-1]] = summary

    summaries = {
        class_id: ClassSummary(
            class_id=class_id,
            bases=builder.bases,
            methods=MappingProxyType(dict(builder.methods)),
        )
        for class_id, builder in builders.items()
    }
    return InheritanceIndex(summaries)


class _ImportCollector(cst.CSTVisitor):
    def __init__(self, source: InheritanceSource, module_aliases: Mapping[str, str]) -> None:
        self.source = source
        self.module_aliases = module_aliases
        self.imported_classes: Dict[str, ClassId] = {}
        self.imported_modules: Dict[str, str] = {}

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        if isinstance(node.names, cst.ImportStar):
            return
        module = _absolute_import_module(node, self.source)
        if module is None:
            return
        module = _canonical_module(module, self.module_aliases)
        for alias in node.names:
            imported_name = _dotted_name(alias.name)
            if imported_name is None:
                continue
            local_name = (
                alias.asname.name.value
                if alias.asname is not None and isinstance(alias.asname.name, cst.Name)
                else imported_name.rsplit(".", 1)[-1]
            )
            self.imported_classes[local_name] = ClassId(module, tuple(imported_name.split(".")))

    def visit_Import(self, node: cst.Import) -> None:
        for alias in node.names:
            imported_module = _dotted_name(alias.name)
            if imported_module is None:
                continue
            local_name = (
                alias.asname.name.value
                if alias.asname is not None and isinstance(alias.asname.name, cst.Name)
                else imported_module.split(".", 1)[0]
            )
            self.imported_modules[local_name] = _canonical_module(imported_module, self.module_aliases)

    def resolve_base(self, node: cst.BaseExpression, child: ClassId) -> Optional[ClassId]:
        if isinstance(node, cst.Name):
            if node.value in self.imported_classes:
                return self.imported_classes[node.value]
            return ClassId(child.module, (*child.qualname[:-1], node.value))
        if isinstance(node, cst.Attribute):
            parts = _attribute_parts(node)
            if not parts:
                return None
            if parts[0] in self.imported_modules:
                return ClassId(self.imported_modules[parts[0]], tuple(parts[1:]))
            if parts[0] in self.imported_classes:
                imported = self.imported_classes[parts[0]]
                return ClassId(imported.module, (*imported.qualname, *parts[1:]))
            return ClassId(child.module, (*child.qualname[:-1], *parts))
        return None


def _summarize_method(annotation: AnnoValue) -> Optional[MethodSummary]:
    definitions = []
    arities = set()
    has_variadic = False
    is_richer = False
    for candidate in [annotation.type_info, *annotation.overloads, *annotation.mp_available]:
        if candidate is None or not isinstance(candidate.def_node, cst.FunctionDef):
            continue
        node = candidate.def_node
        definitions.append(_code(node).strip())
        arity = _parameter_arity(node.params)
        has_variadic = has_variadic or arity is None
        if arity is not None:
            arities.add(arity)
        decorators = tuple(_code(decorator.decorator).strip() for decorator in node.decorators)
        compatible = all(decorator.split("(", 1)[0].rsplit(".", 1)[-1] in {"mp_available", "overload"} for decorator in decorators)
        returns = _code(node.returns.annotation).strip() if node.returns is not None else None
        is_richer = is_richer or (compatible and (not _is_unknown_parameters(_code(node.params).strip()) or not _is_weak_return(returns)))
    if not definitions:
        return None
    fingerprint = hashlib.sha256("\n".join(sorted(set(definitions))).encode("utf-8")).hexdigest()
    return MethodSummary(
        is_richer_than_placeholder=is_richer,
        arities=None if has_variadic else frozenset(arities),
        fingerprint=fingerprint,
    )


def _parameter_arity(params: cst.Parameters) -> Optional[int]:
    if isinstance(params.star_arg, cst.Param) or params.star_kwarg is not None:
        return None
    return len(params.posonly_params) + len(params.params) + len(params.kwonly_params)


def _is_unknown_parameters(parameters: str) -> bool:
    return parameters in _UNKNOWN_PARAMETERS or _INSPECT_PLACEHOLDER.fullmatch(parameters) is not None


def _is_weak_return(returns: Optional[str]) -> bool:
    return returns is None or returns.rsplit(".", 1)[-1] in _WEAK_RETURNS


def _normalize_module(module: str) -> str:
    return module.removesuffix(".__init__")


def _canonical_module(module: str, aliases: Mapping[str, str]) -> str:
    module = _normalize_module(module)
    for source_module in sorted(aliases, key=len, reverse=True):
        if module == source_module:
            return aliases[source_module]
        if module.startswith(f"{source_module}."):
            return f"{aliases[source_module]}{module[len(source_module) :]}"
    return module


def _absolute_import_module(node: cst.ImportFrom, source: InheritanceSource) -> Optional[str]:
    imported_module = _dotted_name(node.module) if node.module is not None else ""
    if not node.relative:
        return imported_module or None

    source_module = _normalize_module(source.source_module)
    package_parts = source_module.split(".") if source.path.stem == "__init__" else source_module.split(".")[:-1]
    levels_up = len(node.relative) - 1
    if levels_up > len(package_parts):
        return None
    if levels_up:
        package_parts = package_parts[:-levels_up]
    if imported_module:
        package_parts.extend(imported_module.split("."))
    return ".".join(package_parts)


def _dotted_name(node: Optional[cst.CSTNode]) -> Optional[str]:
    if isinstance(node, cst.Name):
        return node.value
    if isinstance(node, cst.Attribute):
        parts = _attribute_parts(node)
        return ".".join(parts) if parts else None
    return None


def _attribute_parts(node: cst.BaseExpression) -> Optional[Tuple[str, ...]]:
    if isinstance(node, cst.Name):
        return (node.value,)
    if isinstance(node, cst.Attribute):
        parent = _attribute_parts(node.value)
        return (*parent, node.attr.value) if parent is not None else None
    return None
