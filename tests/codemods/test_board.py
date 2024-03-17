from __future__ import annotations
import pytest
import libcst as cst
import libcst.codemod as codemod
from pathlib import Path
from textwrap import dedent

import stubber.codemod.board as board
from stubber.codemod.board import CreateStubsCodemod, CreateStubsVariant
from stubber.codemod.modify_list import ListChangeSet
from stubber.codemod._partials import Partial


# mark all tests
pytestmark = [pytest.mark.stubber, pytest.mark.codemod, pytest.mark.minify]


@pytest.fixture
def create_stubs() -> cst.Module:
    path = Path(__file__).parent.parent.parent / "src" / "stubber" / "board" / "createstubs.py"
    return cst.parse_module(path.read_text())


@pytest.fixture
def context(create_stubs) -> codemod.CodemodContext:
    return codemod.CodemodContext()


@pytest.fixture
def low_memory_mod(context) -> CreateStubsCodemod:
    return CreateStubsCodemod(context, variant=CreateStubsVariant.MEM)


@pytest.fixture
def low_memory_result(create_stubs, low_memory_mod) -> cst.Module:
    return low_memory_mod.transform_module(create_stubs)


@pytest.fixture
def db_mod(context) -> CreateStubsCodemod:
    return CreateStubsCodemod(context, variant=CreateStubsVariant.DB)


@pytest.fixture
def db_result(create_stubs, db_mod) -> cst.Module:
    return db_mod.transform_module(create_stubs)


def dedent_lines(body: str) -> str:
    lines = [dedent(l) for l in body.splitlines(keepends=True)]
    return "".join(lines)


def compare_lines(excerpt: str, body: str) -> bool:
    """True if all lines in the excerpt are in the body, ignoring leading whitespace"""	
    return dedent_lines(excerpt) in dedent_lines(body)


def test_custom_modules(context, create_stubs):
    ctx = context
    base_module = create_stubs
    mod = CreateStubsCodemod(
        ctx,
        modules=ListChangeSet.from_strings(add=["mycustommodule"], replace=True),
    ).transform_module(base_module)
    assert "mycustommodule" in mod.code


def test_custom_modules_problematic(context, create_stubs):
    ctx = context
    base_module = create_stubs
    mod = CreateStubsCodemod(
        ctx,
        modules=ListChangeSet.from_strings(add=["coolmod"], replace=True),
        problematic=ListChangeSet.from_strings(add=["runt"], replace=True),
    )
    res = mod.transform_module(base_module)
    assert compare_lines('"runt"', res.code)
    assert compare_lines('"coolmod"', res.code)


def test_custom_modules_problematic_excluded(context, create_stubs):
    ctx = context
    base_module = create_stubs

    mod = CreateStubsCodemod(
        ctx,
        modules=ListChangeSet.from_strings(add=["coolmod"], replace=True),
        problematic=ListChangeSet.from_strings(add=["runt"], replace=True),
        excluded=ListChangeSet.from_strings(remove=["webrepl", "_webrepl"], add=["myexclude"]),
    )
    res = mod.transform_module(base_module)
    assert compare_lines('"runt"', res.code)
    assert compare_lines('"coolmod"', res.code)
    assert not compare_lines('"webrepl"', res.code)
    assert not compare_lines('"_webrepl"', res.code)
    assert compare_lines('"myexclude"', res.code)


def test_low_mem_module_doc(low_memory_result):
    # do not match on trailing quotes as ther may be something appended
    assert board._LOW_MEM_MODULE_DOC[-4] in low_memory_result.code


def test_low_mem_read_stubs(low_memory_result):
    assert compare_lines(
        Partial.MODULES_READER.contents(),
        low_memory_result.code,
    )


def test_low_mem_custom_modules(context, create_stubs):
    # this reads from module list, so wont do anything
    # but it shouldnt fail either.
    ctx = context
    base_module = create_stubs

    res = CreateStubsCodemod(
        ctx,
        variant=CreateStubsVariant.MEM,
        modules=ListChangeSet.from_strings(
            add=["supercoolmodule"],
            replace=True,
        ),
    ).transform_module(base_module)
    assert res.code
    assert not compare_lines("'supercoolmodule'", res.code)


def test_lvgl_modules_default(context, create_stubs):
    ctx = context
    base_module = create_stubs
    res = CreateStubsCodemod(
        ctx,
        variant=CreateStubsVariant.LVGL,
    ).transform_module(base_module)
    assert compare_lines('"io", "lodepng", "rtch", "lvgl"', res.code)


def test_lvgl_modules_custom(context, create_stubs):
    ctx = context
    base_module = create_stubs
    cm = CreateStubsCodemod(
        ctx,
        variant=CreateStubsVariant.LVGL,
        modules=ListChangeSet.from_strings(add=["supercoolmodule"], replace=True),
    )
    res = cm.transform_module(base_module)
    assert compare_lines('"supercoolmodule"', res.code)


def test_db_module_doc(db_result):
    assert compare_lines("reads the list of modules", db_result.code)


def test_db_entry(db_result):
    assert compare_lines("was_running = True", db_result.code)
