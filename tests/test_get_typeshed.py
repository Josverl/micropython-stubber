"""
Tests for the get_typeshed module.
"""

import textwrap
from pathlib import Path
from typing import Dict

import pytest

import stubber.get_typeshed as get_typeshed
from stubber.get_typeshed import (
    MICROPYTHON_STDLIB_MODULES,
    _DocstringInjector,
    _get_module_docstrings,
    _pyright_typeshed_path,
    get_typeshed_stubs,
)

pytestmark = [pytest.mark.stubber]


# ---------------------------------------------------------------------------
# _pyright_typeshed_path
# ---------------------------------------------------------------------------


def test_pyright_typeshed_path_returns_existing_path():
    """typeshed stdlib path must exist and be a directory when pyright is available."""
    result = _pyright_typeshed_path()
    assert result is not None, "Expected pyright to be installed in the test environment"
    assert result.is_dir(), f"Expected a directory, got {result}"
    # Must at least contain json.pyi or json/
    has_json = (result / "json.pyi").exists() or (result / "json").is_dir()
    assert has_json, "Expected json module in typeshed stdlib"


def test_pyright_typeshed_path_without_pyright(monkeypatch):
    """Returns None when pyright cannot be imported."""
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pyright":
            raise ImportError("mocked missing pyright")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    # Clear any cached module entry
    import sys

    saved = sys.modules.pop("pyright", None)
    try:
        result = get_typeshed._pyright_typeshed_path()
        assert result is None
    finally:
        if saved is not None:
            sys.modules["pyright"] = saved


# ---------------------------------------------------------------------------
# _get_module_docstrings
# ---------------------------------------------------------------------------


def test_get_module_docstrings_json():
    """Docstrings for json module should include module-level and function-level docs."""
    docs = _get_module_docstrings("json")
    assert "" in docs, "Expected module-level docstring"
    assert "json" in docs[""].lower() or "javascript" in docs[""].lower()
    assert "dumps" in docs, "Expected docstring for json.dumps"
    assert "loads" in docs, "Expected docstring for json.loads"


def test_get_module_docstrings_sys():
    """Docstrings for sys module should be extractable."""
    docs = _get_module_docstrings("sys")
    # sys may not have a module docstring but should have some members
    assert isinstance(docs, dict)


def test_get_module_docstrings_nonexistent():
    """Non-existent module returns empty dict without raising."""
    docs = _get_module_docstrings("_nonexistent_module_xyz_12345")
    assert docs == {}


# ---------------------------------------------------------------------------
# _DocstringInjector
# ---------------------------------------------------------------------------


class TestDocstringInjector:
    """Tests for the LibCST _DocstringInjector transformer."""

    def _run(self, source: str, docstrings: Dict[str, str]) -> str:
        import libcst as cst

        tree = cst.parse_module(textwrap.dedent(source))
        injector = _DocstringInjector(docstrings)
        return tree.visit(injector).code

    # Module-level

    def test_injects_module_docstring(self):
        before = "x: int\n"
        after = self._run(before, {"": "Module doc."})
        assert '"""Module doc."""' in after

    def test_does_not_overwrite_existing_module_docstring(self):
        before = '"""Existing module doc."""\nx: int\n'
        after = self._run(before, {"": "New module doc."})
        assert "Existing module doc." in after
        assert "New module doc." not in after

    # Functions (single-line stub style)

    def test_injects_function_docstring_single_line(self):
        before = "def foo() -> None: ...\n"
        after = self._run(before, {"foo": "Does foo."})
        assert "Does foo." in after
        assert "def foo" in after

    def test_does_not_overwrite_existing_function_docstring(self):
        before = textwrap.dedent("""\
            def foo() -> None:
                \"\"\"Original doc.\"\"\"
                ...
        """)
        after = self._run(before, {"foo": "New doc."})
        assert "Original doc." in after
        assert "New doc." not in after

    def test_injects_function_docstring_indented_block(self):
        before = textwrap.dedent("""\
            def bar() -> None:
                ...
        """)
        after = self._run(before, {"bar": "Does bar."})
        assert "Does bar." in after

    # Classes

    def test_injects_class_docstring(self):
        before = textwrap.dedent("""\
            class Foo:
                x: int
        """)
        after = self._run(before, {"Foo": "Foo class."})
        assert "Foo class." in after

    def test_does_not_overwrite_existing_class_docstring(self):
        before = textwrap.dedent("""\
            class Foo:
                \"\"\"Existing class doc.\"\"\"
                x: int
        """)
        after = self._run(before, {"Foo": "New class doc."})
        assert "Existing class doc." in after
        assert "New class doc." not in after

    def test_injects_method_docstring(self):
        before = textwrap.dedent("""\
            class MyClass:
                def method(self) -> None: ...
        """)
        after = self._run(before, {"MyClass.method": "Method doc."})
        assert "Method doc." in after

    def test_no_docstring_missing_key(self):
        """If a key isn't in the map, nothing should change."""
        before = "def foo() -> None: ...\n"
        after = self._run(before, {"bar": "Bar doc."})
        # foo should still have only the ellipsis body
        assert '"""' not in after


# ---------------------------------------------------------------------------
# get_typeshed_stubs (integration)
# ---------------------------------------------------------------------------


def test_get_typeshed_stubs_copies_modules(tmp_path: Path):
    """get_typeshed_stubs should copy typeshed stubs to the destination."""
    count, skipped = get_typeshed_stubs(tmp_path, modules=["json", "sys"])
    assert count == 2
    assert skipped == []
    # json and sys are both packages in typeshed
    assert (tmp_path / "json").is_dir()
    assert (tmp_path / "sys").is_dir()
    # spot-check: cmath is a single file
    count2, _ = get_typeshed_stubs(tmp_path, modules=["cmath"])
    assert count2 == 1
    assert (tmp_path / "cmath.pyi").is_file()


def test_get_typeshed_stubs_skips_missing(tmp_path: Path):
    """Non-existent modules should appear in the skipped list."""
    count, skipped = get_typeshed_stubs(tmp_path, modules=["json", "_not_a_real_module_xyz"])
    assert count == 1
    assert "_not_a_real_module_xyz" in skipped


def test_get_typeshed_stubs_ai_enhance(tmp_path: Path):
    """With ai_enhance=True the stubs should have module-level docstrings injected."""
    count, skipped = get_typeshed_stubs(tmp_path, modules=["json"], ai_enhance=True)
    assert count == 1
    init_pyi = tmp_path / "json" / "__init__.pyi"
    content = init_pyi.read_text()
    # The CPython json module has a well-known docstring
    assert '"""' in content, "Expected a docstring to have been injected"


def test_get_typeshed_stubs_default_modules(tmp_path: Path):
    """Calling without explicit modules uses MICROPYTHON_STDLIB_MODULES."""
    count, skipped = get_typeshed_stubs(tmp_path)
    # At least some modules should be copied
    assert count > 0
    # None of the default modules should fail unless typeshed layout changed
    # (allow a few failures for very rare edge cases)
    assert count >= len(MICROPYTHON_STDLIB_MODULES) - 3


def test_get_typeshed_stubs_no_pyright(tmp_path: Path, monkeypatch):
    """Should raise RuntimeError if pyright is not available."""
    monkeypatch.setattr(get_typeshed, "_pyright_typeshed_path", lambda: None)
    with pytest.raises(RuntimeError, match="pyright"):
        get_typeshed_stubs(tmp_path, modules=["json"])


# ---------------------------------------------------------------------------
# Command-line integration
# ---------------------------------------------------------------------------


def test_cli_get_typeshed(tmp_path: Path):
    """CLI command should copy stubs and exit cleanly."""
    from click.testing import CliRunner

    from stubber.commands.get_typeshed_cmd import cli_get_typeshed

    runner = CliRunner()
    result = runner.invoke(
        cli_get_typeshed,
        ["--stub-path", str(tmp_path), "-m", "json", "--no-format"],
    )
    assert result.exit_code == 0, result.output
    assert (tmp_path / "json").is_dir()


def test_cli_get_typeshed_list_modules():
    """--list-modules should print the default list and exit 0."""
    from click.testing import CliRunner

    from stubber.commands.get_typeshed_cmd import cli_get_typeshed

    runner = CliRunner()
    result = runner.invoke(cli_get_typeshed, ["--list-modules"])
    assert result.exit_code == 0
    assert "json" in result.output
    assert "sys" in result.output


def test_cli_get_typeshed_ai_enhance(tmp_path: Path):
    """--ai-enhance flag should produce enriched stubs."""
    from click.testing import CliRunner

    from stubber.commands.get_typeshed_cmd import cli_get_typeshed

    runner = CliRunner()
    result = runner.invoke(
        cli_get_typeshed,
        ["--stub-path", str(tmp_path), "-m", "json", "--ai-enhance", "--no-format"],
    )
    assert result.exit_code == 0, result.output
    content = (tmp_path / "json" / "__init__.pyi").read_text()
    assert '"""' in content
