"""Generate MicroPython u-module alias stubs."""

import ast
from pathlib import Path

from mpflash.logger import log


def _public_name(name: str) -> bool:
    return not name.startswith("_")


def _assigned_names(target: ast.expr) -> list[str]:
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.List, ast.Tuple)):
        return [name for item in target.elts for name in _assigned_names(item)]
    return []


def _static_all(statements: list[ast.stmt]) -> list[str] | None:
    for statement in statements:
        if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
            continue
        targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
        if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in targets):
            continue
        value = statement.value
        if not isinstance(value, (ast.List, ast.Tuple)):
            return None
        names = [item.value for item in value.elts if isinstance(item, ast.Constant) and isinstance(item.value, str)]
        return names if len(names) == len(value.elts) else None
    return None


def _declared_names(statements: list[ast.stmt]) -> list[str]:
    names: list[str] = []
    for statement in statements:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(statement.name)
        elif isinstance(statement, ast.Assign):
            for target in statement.targets:
                names.extend(_assigned_names(target))
        elif isinstance(statement, ast.AnnAssign):
            names.extend(_assigned_names(statement.target))
        elif isinstance(statement, (ast.Import, ast.ImportFrom)):
            for alias in statement.names:
                if alias.name != "*" and alias.asname == alias.name:
                    names.append(alias.name)
        elif isinstance(statement, ast.If):
            names.extend(_declared_names(statement.body))
            names.extend(_declared_names(statement.orelse))
        elif isinstance(statement, ast.Try):
            names.extend(_declared_names(statement.body))
            names.extend(_declared_names(statement.orelse))
            names.extend(_declared_names(statement.finalbody))
            for handler in statement.handlers:
                names.extend(_declared_names(handler.body))
        elif isinstance(statement, ast.Match):
            for case in statement.cases:
                names.extend(_declared_names(case.body))
    return names


def public_stub_names(stub_path: Path) -> list[str]:
    """Return the public names exported by a stub module."""
    module = ast.parse(stub_path.read_text(encoding="utf-8"), filename=str(stub_path))
    names = _static_all(module.body)
    if names is None:
        names = [name for name in _declared_names(module.body) if _public_name(name)]
    return list(dict.fromkeys(names))


def _canonical_stub(target_folder: Path, module_name: str) -> Path | None:
    for candidate in (target_folder / f"{module_name}.pyi", target_folder / module_name / "__init__.pyi"):
        if candidate.is_file():
            return candidate
    return None


def write_umodule_stub(target_folder: Path, module_name: str) -> Path:
    """Write a u-module stub that explicitly re-exports its canonical module."""
    target = target_folder / f"u{module_name}.pyi"
    lines = [f"# This umodule is a MicroPython reference to {module_name}"]
    canonical = _canonical_stub(target_folder, module_name)
    if canonical is None:
        log.warning(f"Canonical stub for {module_name} not found in {target_folder}; using a wildcard alias")
        lines.append(f"from {module_name} import *")
    else:
        lines.extend(f"from {module_name} import {name} as {name}" for name in public_stub_names(canonical))
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target
