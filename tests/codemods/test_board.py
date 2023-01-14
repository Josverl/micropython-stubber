from __future__ import annotations
import pytest
import libcst as cst
import libcst.codemod as codemod
from pathlib import Path
from textwrap import dedent

import stubber.codemod.board as board
from stubber.codemod.board import CreateStubsCodemod, CreateStubsFlavor
from stubber.codemod.modify_list import ListChangeSet


@pytest.fixture
def create_stubs() -> cst.Module:
    path = Path(__file__).parent.parent.parent / "board" / "createstubs.py"
    return cst.parse_module(path.read_text())


@pytest.fixture
def context(create_stubs) -> tuple[codemod.CodemodContext, cst.Module]:
    return codemod.CodemodContext(), create_stubs


@pytest.fixture
def low_memory_mod(context) -> CreateStubsCodemod:
    return CreateStubsCodemod(context[0], flavor=CreateStubsFlavor.LOW_MEM)


@pytest.fixture
def low_memory_result(context, low_memory_mod) -> cst.Module:
    return low_memory_mod.transform_module(context[1])


def dedent_lines(body: str) -> str:
    lines = [dedent(l) for l in body.splitlines(keepends=True)]
    return "".join(lines)


def compare_lines(excerpt: str, body: str) -> bool:
    return dedent_lines(excerpt) in dedent_lines(body)


def test_custom_modules(context):
    ctx, cont = context
    mod = CreateStubsCodemod(ctx, modules=ListChangeSet.from_strings(add=["mycustommodule"], replace=True)).transform_module(cont)
    assert "mycustommodule" in mod.code


def test_custom_modules__problematic(context):
    mod = CreateStubsCodemod(
        context[0],
        modules=ListChangeSet.from_strings(add=["coolmod"], replace=True),
        problematic=ListChangeSet.from_strings(add=["runt"], replace=True),
    )
    res = mod.transform_module(context[1])
    assert compare_lines('"runt"', res.code)
    assert compare_lines('"coolmod"', res.code)


def test_custom_modules__problematic_excluded(context):
    mod = CreateStubsCodemod(
        context[0],
        modules=ListChangeSet.from_strings(add=["coolmod"], replace=True),
        problematic=ListChangeSet.from_strings(add=["runt"], replace=True),
        excluded=ListChangeSet.from_strings(remove=["webrepl", "_webrepl"], add=["myexclude"]),
    )
    res = mod.transform_module(context[1])
    assert compare_lines('"runt"', res.code)
    assert compare_lines('"coolmod"', res.code)
    assert not compare_lines('"webrepl"', res.code)
    assert not compare_lines('"_webrepl"', res.code)
    assert compare_lines('"myexclude"', res.code)


def test_low_mem__module_doc(low_memory_result):
    assert board._LOW_MEM_MODULE_DOC in low_memory_result.code


def test_low_mem__read_stubs(low_memory_result):
    assert compare_lines(board._MODULES_READER, low_memory_result.code)


def test_low_mem__custom_modules(context):
    # this reads from module list, so wont do anything
    # but it shouldnt fail either.
    res = CreateStubsCodemod(
        context[0], flavor=CreateStubsFlavor.LOW_MEM, modules=ListChangeSet.from_strings(add=["supercoolmodule"], replace=True)
    ).transform_module(context[1])
    assert res.code
    assert not compare_lines("'supercoolmodule'", res.code)


def test_lvgl__init(context):
    res = CreateStubsCodemod(context[0], flavor=CreateStubsFlavor.LVGL).transform_module(context[1])
    assert compare_lines(board._LVGL_MAIN, res.code)


def test_lvgl__modules_default(context):
    res = CreateStubsCodemod(context[0], flavor=CreateStubsFlavor.LVGL).transform_module(context[1])
    assert compare_lines('"io", "lodepng", "rtch", "lvgl"', res.code)


def test_lvgl__modules_custom(context):
    res = CreateStubsCodemod(
        context[0], flavor=CreateStubsFlavor.LVGL, modules=ListChangeSet.from_strings(add=["supercoolmodule"], replace=True)
    ).transform_module(context[1])
    assert compare_lines('"supercoolmodule"', res.code)
