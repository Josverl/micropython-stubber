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


def test_stub_header_has_asyncgenerator_import(createstubs, tmp_path):
    """Generated stub files should import AsyncGenerator from typing."""
    stubber = createstubs.Stubber(path=str(tmp_path), firmware_id="test-fw")
    stubber.report_start()
    stub_path = str(tmp_path / "json.pyi")
    stubber.create_module_stub("json", stub_path)

    content = Path(stub_path).read_text()
    assert "AsyncGenerator" in content, "stub file should import AsyncGenerator"
