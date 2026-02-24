"""
Extract typeshed stdlib stubs from the bundled pyright package and optionally
enrich them with CPython docstrings from the runtime.

These can then be used as a source for the MergeCommand codemod to enrich
MicroPython stubs with better type information and docstrings.

The typeshed stubs bundled with pyright do not include docstrings by design
(typeshed policy is to keep stubs minimal for maintainability).  When
``ai_enhance=True`` is requested the module will additionally extract
docstrings from the running CPython interpreter and inject them into the
copied stubs so that IDE tooling (e.g. Pylance / Pyright) can show
documentation for MicroPython stdlib-compatible modules.
"""

import inspect
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import libcst as cst
from mpflash.logger import log

# ---------------------------------------------------------------------------
# Modules known to be compatible between MicroPython and CPython stdlib.
# These are the only ones we want to copy / enrich.
# ---------------------------------------------------------------------------
MICROPYTHON_STDLIB_MODULES: List[str] = [
    "array",
    "binascii",
    "cmath",
    "collections",
    "errno",
    "gc",
    "hashlib",
    "io",
    "json",
    "math",
    "os",
    "random",
    "re",
    "select",
    "socket",
    "ssl",
    "struct",
    "sys",
    "time",
    "zlib",
]
"""
Modules that exist in both MicroPython and CPython stdlib and are safe to
copy type information from typeshed.
"""


# ---------------------------------------------------------------------------
# Helper: locate the typeshed stdlib folder inside the pyright package
# ---------------------------------------------------------------------------


def _pyright_typeshed_path() -> Optional[Path]:
    """
    Return the path to the ``stdlib`` directory bundled inside the ``pyright``
    Python package, or *None* if the package cannot be found.

    The ``pyright`` pip package wraps the npm package and bundles the
    typeshed fallback stubs at a fixed relative location.
    """
    try:
        import pyright as _pyright  # local import so the rest of the module works without it
    except ImportError:
        log.warning("pyright package not found – cannot extract typeshed stubs")
        return None

    pkg_root = Path(_pyright.__file__).parent
    # pyright pip package layout: pyright/dist/dist/typeshed-fallback/stdlib
    typeshed_stdlib = pkg_root / "dist" / "dist" / "typeshed-fallback" / "stdlib"
    if typeshed_stdlib.exists():
        return typeshed_stdlib

    log.warning(f"typeshed stdlib not found in expected location: {typeshed_stdlib}")
    return None


# ---------------------------------------------------------------------------
# Helper: extract CPython docstrings via runtime introspection
# ---------------------------------------------------------------------------


def _extract_cpython_docstring(module_name: str, obj_path: str) -> Optional[str]:
    """
    Try to retrieve the CPython docstring for a dotted object path within
    a module.  Returns *None* if the object cannot be found or has no doc.

    Args:
        module_name: top-level module name, e.g. ``"json"``
        obj_path: dotted path within the module, e.g. ``"dumps"`` or
                  ``"JSONDecoder.decode"``
    """
    try:
        mod = sys.modules.get(module_name) or __import__(module_name)
        obj: object = mod
        for part in obj_path.split("."):
            obj = getattr(obj, part, None)
            if obj is None:
                return None
        return inspect.getdoc(obj) or None
    except Exception:
        return None


def _get_module_docstrings(module_name: str) -> Dict[str, str]:
    """
    Return a mapping of *object_path -> docstring* for all public objects in
    the given module using CPython runtime introspection.

    Args:
        module_name: Name of the stdlib module, e.g. ``"json"``

    Returns:
        A dict whose keys are dotted names relative to the module
        (e.g. ``""`` for the module itself, ``"dumps"`` for a function,
        ``"JSONDecoder"`` for a class, ``"JSONDecoder.decode"`` for a method).
    """
    docs: Dict[str, str] = {}
    try:
        mod = __import__(module_name)
    except ImportError:
        log.debug(f"Cannot import module {module_name!r} – skipping docstring extraction")
        return docs

    # Module-level docstring
    mod_doc = inspect.getdoc(mod)
    if mod_doc:
        docs[""] = mod_doc

    for name in dir(mod):
        if name.startswith("_"):
            continue
        obj = getattr(mod, name, None)
        if obj is None:
            continue

        # Functions / built-in functions
        if callable(obj) and not isinstance(obj, type):
            doc = inspect.getdoc(obj)
            if doc:
                docs[name] = doc

        # Classes
        elif isinstance(obj, type):
            class_doc = inspect.getdoc(obj)
            if class_doc:
                docs[name] = class_doc
            # class methods
            for mname in dir(obj):
                if mname.startswith("_") and mname not in ("__init__", "__call__"):
                    continue
                mobj = getattr(obj, mname, None)
                if mobj is None:
                    continue
                if callable(mobj):
                    mdoc = inspect.getdoc(mobj)
                    if mdoc:
                        docs[f"{name}.{mname}"] = mdoc

    return docs


# ---------------------------------------------------------------------------
# LibCST transformer: inject docstrings into a .pyi stub
# ---------------------------------------------------------------------------


class _DocstringInjector(cst.CSTTransformer):
    """
    LibCST transformer that injects docstrings into a stub file.

    It only *adds* docstrings; it never overwrites an existing docstring
    (the MicroPython-specific documentation takes priority).
    """

    def __init__(self, docstrings: Dict[str, str]):
        """
        Args:
            docstrings: mapping produced by :func:`_get_module_docstrings`
        """
        self._docs = docstrings
        self._class_stack: List[str] = []

    # --- helpers ---

    def _make_docstring_node(self, text: str) -> cst.SimpleStatementLine:
        """Build a CST node for a triple-quoted docstring statement."""
        # Escape any triple double-quotes inside the text to avoid syntax errors.
        # Replace """ with \" \" \" (each individual quote escaped).
        safe_text = text.replace('"""', r'\"\"\"')
        return cst.parse_statement(f'"""{safe_text}"""\n')  # type: ignore[return-value]

    def _has_docstring(self, body: cst.BaseSuite) -> bool:
        """Return True if the first statement in *body* is already a docstring."""
        if not isinstance(body, cst.IndentedBlock):
            return False
        stmts = body.body
        if not stmts:
            return False
        first = stmts[0]
        if not isinstance(first, cst.SimpleStatementLine):
            return False
        if not first.body:
            return False
        expr = first.body[0]
        if not isinstance(expr, cst.Expr):
            return False
        return isinstance(expr.value, (cst.SimpleString, cst.ConcatenatedString, cst.FormattedString))

    # --- module ---

    def visit_Module(self, node: cst.Module) -> bool:
        return True

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        if "" not in self._docs:
            return updated_node
        stmts = list(updated_node.body)
        if not stmts:
            return updated_node
        # Check if there is already a docstring at the top
        first = stmts[0]
        if isinstance(first, cst.SimpleStatementLine) and first.body:
            expr = first.body[0]
            if isinstance(expr, cst.Expr) and isinstance(expr.value, (cst.SimpleString, cst.ConcatenatedString)):
                return updated_node  # already has a docstring
        # Prepend the docstring
        try:
            ds_node = self._make_docstring_node(self._docs[""])
            updated_node = updated_node.with_changes(body=[ds_node, *stmts])
        except Exception as exc:
            log.debug(f"Could not inject module docstring: {exc}")
        return updated_node

    # --- functions ---

    def _leave_funcdef(self, updated_node: cst.FunctionDef, qualified_name: str) -> cst.FunctionDef:
        if qualified_name not in self._docs:
            return updated_node
        if self._has_docstring(updated_node.body):
            return updated_node  # preserve existing
        doc_text = self._docs[qualified_name]
        try:
            ds_node = self._make_docstring_node(doc_text)
            old_body = updated_node.body
            if isinstance(old_body, cst.IndentedBlock):
                # Replace ... / pass with the docstring
                new_body = old_body.with_changes(body=[ds_node])
                updated_node = updated_node.with_changes(body=new_body)
            elif isinstance(old_body, cst.SimpleStatementSuite):
                # Single-line stub: def f(): ...
                # Convert to indented block with docstring then ellipsis
                new_body = cst.IndentedBlock(
                    body=[
                        ds_node,
                        cst.SimpleStatementLine(
                            body=[cst.Expr(value=cst.Ellipsis())],
                        ),
                    ]
                )
                updated_node = updated_node.with_changes(body=new_body)
        except Exception as exc:
            log.debug(f"Could not inject docstring for {qualified_name!r}: {exc}")
        return updated_node

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.BaseStatement:
        fn_name = updated_node.name.value
        if self._class_stack:
            qualified = f"{self._class_stack[-1]}.{fn_name}"
        else:
            qualified = fn_name
        return self._leave_funcdef(updated_node, qualified)

    # --- classes ---

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        self._class_stack.append(node.name.value)
        return True

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.BaseStatement:
        cls_name = self._class_stack.pop() if self._class_stack else updated_node.name.value
        if cls_name not in self._docs:
            return updated_node
        if self._has_docstring(updated_node.body):
            return updated_node
        doc_text = self._docs[cls_name]
        try:
            ds_node = self._make_docstring_node(doc_text)
            old_body = updated_node.body
            if isinstance(old_body, cst.IndentedBlock):
                new_body = old_body.with_changes(body=[ds_node, *old_body.body])
                updated_node = updated_node.with_changes(body=new_body)
        except Exception as exc:
            log.debug(f"Could not inject docstring for class {cls_name!r}: {exc}")
        return updated_node


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_typeshed_stubs(
    dest_path: Path,
    modules: Optional[List[str]] = None,
    ai_enhance: bool = False,
) -> Tuple[int, List[str]]:
    """
    Copy typeshed stdlib ``.pyi`` files for MicroPython-compatible modules to
    *dest_path*.  When *ai_enhance* is ``True`` the copies are additionally
    enriched with docstrings extracted from the running CPython interpreter.

    Args:
        dest_path:   Destination directory (will be created if missing).
        modules:     List of module names to copy.  Defaults to
                     :data:`MICROPYTHON_STDLIB_MODULES`.
        ai_enhance:  When ``True``, inject CPython docstrings into the
                     copied stubs before writing them.

    Returns:
        A tuple ``(count, skipped)`` where *count* is the number of modules
        copied and *skipped* is a list of module names that could not be found
        in the typeshed.
    """
    if modules is None:
        modules = MICROPYTHON_STDLIB_MODULES

    typeshed_stdlib = _pyright_typeshed_path()
    if typeshed_stdlib is None:
        raise RuntimeError("Cannot locate typeshed stubs – is the 'pyright' package installed?")

    dest_path = Path(dest_path)
    dest_path.mkdir(parents=True, exist_ok=True)

    count = 0
    skipped: List[str] = []

    for module_name in modules:
        # Try single-file module first (e.g. cmath.pyi)
        single_file = typeshed_stdlib / f"{module_name}.pyi"
        # Then try package (e.g. json/__init__.pyi)
        pkg_dir = typeshed_stdlib / module_name

        if single_file.exists():
            _copy_and_enrich(single_file, dest_path / f"{module_name}.pyi", module_name, ai_enhance)
            count += 1
            log.debug(f"  Copied {module_name}.pyi from typeshed")
        elif pkg_dir.exists() and pkg_dir.is_dir() and (pkg_dir / "__init__.pyi").exists():
            dest_pkg = dest_path / module_name
            dest_pkg.mkdir(exist_ok=True)
            for src_file in sorted(pkg_dir.rglob("*.pyi")):
                rel = src_file.relative_to(pkg_dir)
                dst_file = dest_pkg / rel
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                # For __init__.pyi, inject module-level docs; for sub-files use None
                mod_name_for_docs = module_name if rel.name == "__init__.pyi" else None
                _copy_and_enrich(src_file, dst_file, mod_name_for_docs, ai_enhance)
            count += 1
            log.debug(f"  Copied {module_name}/ package from typeshed")
        else:
            log.warning(f"  Module {module_name!r} not found in typeshed stdlib – skipping")
            skipped.append(module_name)

    return count, skipped


def _copy_and_enrich(src: Path, dst: Path, module_name: Optional[str], ai_enhance: bool) -> None:
    """
    Copy *src* to *dst*.  When *ai_enhance* is ``True`` and *module_name* is
    provided, inject CPython docstrings using LibCST before writing.
    """
    source_text = src.read_text(encoding="utf-8")

    if ai_enhance and module_name:
        log.debug(f"    AI-enhancing {module_name}...")
        docstrings = _get_module_docstrings(module_name)
        if docstrings:
            try:
                tree = cst.parse_module(source_text)
                injector = _DocstringInjector(docstrings)
                new_tree = tree.visit(injector)
                source_text = new_tree.code
            except Exception as exc:
                log.warning(f"    DocstringInjector failed for {module_name!r}: {exc} – using raw stub")

    dst.write_text(source_text, encoding="utf-8")
