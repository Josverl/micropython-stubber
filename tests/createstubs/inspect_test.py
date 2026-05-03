# type: ignore reportGeneralTypeIssues
"""Tests for inspect module integration in createstubs."""
import sys
from pathlib import Path
from typing import Generator

import pytest

from shared import import_variant

pytestmark = [pytest.mark.stubber, pytest.mark.micropython]


@pytest.fixture
def createstubs(mock_micropython_path):
    return import_variant("board", "createstubs")


@pytest.fixture
def stubber_instance(createstubs, tmp_path):
    return createstubs.Stubber(path=str(tmp_path), firmware_id="test-fw")


def _write_stub_for(stubber, module_obj, tmp_path) -> str:
    """Helper: write stubs for a mock module object and return the content."""
    stub_file = tmp_path / "test.pyi"
    with open(stub_file, "w") as fp:
        fp.write(
            "from __future__ import annotations\n"
            "from typing import Any, Final, Generator, AsyncGenerator\n"
            "from _typeshed import Incomplete\n\n"
        )
        stubber.write_object_stub(fp, module_obj, "mock", "")
    return stub_file.read_text()


# ---------------------------------------------------------------------------
# Helpers to build mock modules
# ---------------------------------------------------------------------------


def _make_mock_module(**attrs):
    """Create a simple mock module-like object with given attributes."""

    class _MockModule:
        pass

    m = _MockModule()
    for k, v in attrs.items():
        setattr(m, k, v)
    return m


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_has_inspect(createstubs):
    """inspect module should be importable and _has_inspect should be True on CPython."""
    assert createstubs._has_inspect is True, "_has_inspect should be True when running on CPython"


def test_async_function_generates_async_def(stubber_instance, tmp_path):
    """Async functions should generate 'async def' stubs."""

    async def my_coro(x, y):
        return x + y

    mock = _make_mock_module(my_coro=my_coro)
    content = _write_stub_for(stubber_instance, mock, tmp_path)

    assert "async def my_coro" in content, "async function should produce 'async def'"
    assert "def my_coro" in content  # also matched by 'async def', actual prefix check is below
    # Ensure it really starts with 'async def', not just 'def'
    lines = [l.strip() for l in content.splitlines()]
    async_def_lines = [l for l in lines if l.startswith("async def my_coro")]
    assert len(async_def_lines) == 1, "should have exactly one async def my_coro"


def test_async_function_has_correct_params(stubber_instance, tmp_path):
    """Async function stub should include the correct parameter names."""

    async def my_coro(a, b, c):
        pass

    mock = _make_mock_module(my_coro=my_coro)
    content = _write_stub_for(stubber_instance, mock, tmp_path)

    assert "async def my_coro(a, b, c)" in content


def test_regular_function_is_not_async(stubber_instance, tmp_path):
    """Regular functions must not be marked as async."""

    def regular(x, y):
        return x + y

    mock = _make_mock_module(regular=regular)
    content = _write_stub_for(stubber_instance, mock, tmp_path)

    lines = [l.strip() for l in content.splitlines()]
    async_lines = [l for l in lines if l.startswith("async def regular")]
    assert len(async_lines) == 0, "regular function must not become async def"
    plain_lines = [l for l in lines if l.startswith("def regular")]
    assert len(plain_lines) == 1, "regular function should produce plain def"


def test_generator_function_returns_generator(stubber_instance, tmp_path):
    """Generator functions should produce '-> Generator' stubs."""

    def my_gen(n):
        for i in range(n):
            yield i

    mock = _make_mock_module(my_gen=my_gen)
    content = _write_stub_for(stubber_instance, mock, tmp_path)

    assert "def my_gen" in content
    assert "-> Generator" in content, "generator function should have -> Generator return type"


def test_async_generator_function_returns_asyncgenerator(stubber_instance, tmp_path):
    """Async generator functions should produce 'async def ... -> AsyncGenerator' stubs."""

    async def my_async_gen(n):
        for i in range(n):
            yield i

    mock = _make_mock_module(my_async_gen=my_async_gen)
    content = _write_stub_for(stubber_instance, mock, tmp_path)

    lines = [l.strip() for l in content.splitlines()]
    async_gen_lines = [l for l in lines if l.startswith("async def my_async_gen")]
    assert len(async_gen_lines) == 1, "async generator should produce 'async def'"
    assert "-> AsyncGenerator" in content, "async generator should have -> AsyncGenerator return type"


def test_signature_positional_params(stubber_instance, tmp_path):
    """inspect.signature should provide actual parameter names instead of *args, **kwargs."""

    def func_with_params(alpha, beta, gamma):
        pass

    mock = _make_mock_module(func_with_params=func_with_params)
    content = _write_stub_for(stubber_instance, mock, tmp_path)

    # Should have the actual parameter names, not just *args, **kwargs
    assert "func_with_params(alpha, beta, gamma)" in content


def test_signature_with_variadic_params(stubber_instance, tmp_path):
    """Variadic parameters (*args, **kwargs) should be preserved in stub."""

    def variadic(a, *args, **kwargs):
        pass

    mock = _make_mock_module(variadic=variadic)
    content = _write_stub_for(stubber_instance, mock, tmp_path)

    assert "variadic(a, *args, **kwargs)" in content


def test_signature_with_keyword_only_params(stubber_instance, tmp_path):
    """Keyword-only parameters (after bare *) should be emitted with the '*' separator."""

    def kw_only(a, *, b, c=0):
        pass

    mock = _make_mock_module(kw_only=kw_only)
    content = _write_stub_for(stubber_instance, mock, tmp_path)

    assert "kw_only(a, *, b, c" in content, "keyword-only params need '* ' separator"


def test_class_method_no_double_self(stubber_instance, tmp_path):
    """Class methods must not have 'self' duplicated.

    On MicroPython, inspect.signature() uses dummy parameter names (x0, x1, ...),
    so the first parameter is 'x0' rather than 'self'.  The stub generator must
    still strip that first parameter and add exactly one 'self' back.
    This test verifies the resulting stub has no doubled self on CPython, and
    also directly exercises the name-agnostic stripping logic.
    """

    class MyClass:
        def my_method(self, x, y):
            pass

        def no_extra_params(self):
            pass

    mock = _make_mock_module(MyClass=MyClass)
    content = _write_stub_for(stubber_instance, mock, tmp_path)

    # Verify self is not doubled (e.g. "self, self, x, y")
    assert "self, self" not in content, "self must not be duplicated in class methods"
    # The correct stub should have exactly (self, x, y)
    assert "def my_method(self, x, y)" in content
    # A method with only self should produce just "self" without trailing comma issues
    assert "def no_extra_params(self)" in content


def test_method_in_class_has_self(stubber_instance, tmp_path):
    """Methods in classes should have 'self' as first parameter."""

    class MyClass:
        def my_method(self, x, y):
            return x + y

        async def my_async_method(self, z):
            pass

    mock = _make_mock_module(MyClass=MyClass)
    content = _write_stub_for(stubber_instance, mock, tmp_path)

    # Regular method should have self
    assert "def my_method(self, x, y)" in content
    # Async method should be async def with self
    assert "async def my_async_method(self, z)" in content


def test_classmethod_uses_inspect_for_signature(stubber_instance, tmp_path):
    """Classmethods should use inspect to extract the actual parameter signature."""

    class MyClass:
        @classmethod
        def my_classmethod(cls, x, y):
            pass

        @classmethod
        def no_extra_params(cls):
            pass

    mock = _make_mock_module(MyClass=MyClass)
    content = _write_stub_for(stubber_instance, mock, tmp_path)

    # Should have @classmethod decorator
    assert "@classmethod" in content
    # Should use actual parameter names, not *args, **kwargs
    assert "def my_classmethod(cls, x, y)" in content, "classmethod should have actual params from inspect"
    # A classmethod with only cls should produce just 'cls'
    assert "def no_extra_params(cls)" in content
    # cls must not be doubled
    assert "cls, cls" not in content


def test_classmethod_fallback_without_inspect(stubber_instance, tmp_path):
    """Without inspect, classmethods should fall back to cls, *args, **kwargs."""

    class MyClass:
        @classmethod
        def my_classmethod(cls, x, y):
            pass

    stubber_instance._use_inspect = False

    mock = _make_mock_module(MyClass=MyClass)
    content = _write_stub_for(stubber_instance, mock, tmp_path)

    # Should still have @classmethod decorator
    assert "@classmethod" in content
    # Without inspect, should fall back to *args, **kwargs
    assert "def my_classmethod(cls, *args, **kwargs)" in content


def test_stub_header_has_asyncgenerator_import(createstubs, tmp_path):
    """Generated stub files should import AsyncGenerator from typing."""
    stubber = createstubs.Stubber(path=str(tmp_path), firmware_id="test-fw")
    stubber.report_start()
    stub_path = str(tmp_path / "json.pyi")
    stubber.create_module_stub("json", stub_path)

    content = Path(stub_path).read_text()
    assert "AsyncGenerator" in content, "stub file should import AsyncGenerator"


def test_low_mem_mode_skips_inspect_and_docstrings(stubber_instance, tmp_path):
    """Low-memory mode should avoid inspect-based signatures and docstring expansion."""

    def fn_with_doc(alpha, beta):
        """A detailed function docstring that should be omitted in low-memory mode."""
        return alpha + beta

    stubber_instance._is_low_mem_port = True
    stubber_instance._capture_docstrings = False
    stubber_instance._use_inspect = False

    mock = _make_mock_module(fn_with_doc=fn_with_doc)
    content = _write_stub_for(stubber_instance, mock, tmp_path)

    assert "def fn_with_doc(*args, **kwargs)" in content
    assert "A detailed function docstring" not in content
