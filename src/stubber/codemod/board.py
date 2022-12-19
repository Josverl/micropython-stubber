from __future__ import annotations

from enum import Enum, unique, auto
from typing import Optional, Iterator

import libcst as cst
import libcst.codemod as codemod
from libcst import matchers as m

from stubber.codemod.modify_list import ModifyListElements, ListChangeSet
from stubber.cst_transformer import update_module_docstr

_STUBBER_MATCHER = m.Assign(
    targets=[
        m.AssignTarget(
            target=m.Name("stubber"),
        )
    ],
    value=m.Call(func=m.Name("Stubber")),
)

_MODULES_MATCHER = m.Assign(
    targets=[
        m.AssignTarget(
            target=m.Attribute(
                value=m.Name(value="stubber"),
                attr=m.Name(value="modules"),
            ),
        )
    ],
)

_MODULES_READER = """
# Read stubs from modulelist
try:
    with open("modulelist" + ".txt") as f:
        # not optimal , but works on mpremote and eps8266
        stubber.modules = [l.strip() for l in f.read().split("\\n") if len(l.strip()) and l.strip()[0] != "#"]
except OSError:
    # fall back gracefully
    stubber.modules = ["micropython"]
    _log.warning("Warning: modulelist.txt could not be found.")
"""

_LOW_MEM_MODULE_DOC = '''
"""Create stubs for (all) modules on a MicroPython board.

    This variant of the createstubs.py script is optimised for use on low-memory devices, and reads the list of modules from a text file 
    `./modulelist.txt` that should be uploaded to the device.
    If that cannot be found then only a single module (micropython) is stubbed.
    In order to run this on low-memory devices two additioanl steps are recommended: 
    - minifification, using python-minifier
      to reduce overall size, and remove logging overhead.
    - cross compilation, using mpy-cross, 
      to avoid the compilation step on the micropython device 

    you can find a cross-compiled version located here: ./minified/createstubs_mem.mpy
"""
'''

_LVGL_MAIN = """
# Specify firmware name & version
try:
    fw_id = "lvgl-{0}_{1}_{2}-{3}-{4}".format(
        lvgl.version_major(),
        lvgl.version_minor(),
        lvgl.version_patch(),
        lvgl.version_info(),
        sys.platform,
    )
except Exception:
    fw_id = "lvgl-{0}_{1}_{2}_{3}-{4}".format(8, 1, 0, "dev", sys.platform)
    
stubber = Stubber(firmware_id=fw_id)

"""


@unique
class CreateStubsFlavor(Enum):
    """Dictates create stubs target variant."""

    BASE = auto()
    LOW_MEM = auto()
    LVGL = auto()


class SimpleStatementReplace(m.MatcherDecoratableTransformer):
    new_node: cst.SimpleStatementLine
    scope_matcher: m.BaseMatcherNode

    def __init__(self, new_node: cst.SimpleStatementLine, scope_matcher: Optional[m.BaseMatcherNode] = None):
        self.new_node = new_node
        self.scope_matcher = scope_matcher
        if self.scope_matcher:
            self.__class__ = type(
                f"{self.__class__.__name__}_{repr(scope_matcher)}",
                (self.__class__,),
                {"replace_statement": m.call_if_inside(scope_matcher)(self.__class__.replace_statement)},
            )
        super().__init__()

    @m.leave(m.SimpleStatementLine())
    def replace_statement(self, _: cst.SimpleStatementLine, __: cst.SimpleStatementLine) -> cst.SimpleStatementLine:
        return self.new_node


class ReadModulesCodemod(codemod.Codemod):
    """Replaces static modules list with file-load method."""

    modules_reader_node: cst.SimpleStatementLine

    def __init__(self, context: codemod.CodemodContext, reader_node: Optional[cst.SimpleStatementLine] = None):
        super().__init__(context)
        self.modules_reader_node = reader_node or cst.parse_statement(_MODULES_READER)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        transform = SimpleStatementReplace(self.modules_reader_node, scope_matcher=m.SimpleStatementLine(body=[_MODULES_MATCHER]))
        return tree.visit(transform)


class ModuleDocCodemod(codemod.Codemod):
    """Replaces a module's docstring."""

    module_doc: str

    def __init__(self, context: codemod.CodemodContext, module_doc: str):
        super().__init__(context)
        self.module_doc = module_doc

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        if not isinstance(self.module_doc, str):
            raise TypeError(f"Expected module_doc to be of type str, received: {type(self.module_doc)}")
        return update_module_docstr(tree, cst.parse_statement(self.module_doc))


class ModulesUpdateCodemod(codemod.Codemod):
    """Dynamically replace static module list(s)."""

    modules_changeset: ListChangeSet
    problematic_changeset: ListChangeSet
    excluded_changeset: ListChangeSet

    modules_scope: m.BaseMatcherNode = _MODULES_MATCHER
    problematic_scope: m.BaseMatcherNode = m.Assign(
        targets=[m.AssignTarget(target=m.Attribute(value=m.Name("self"), attr=m.Name("problematic")))]
    )
    excluded_scope: m.BaseMatcherNode = m.Assign(
        targets=[m.AssignTarget(target=m.Attribute(value=m.Name("self"), attr=m.Name("excluded")))]
    )

    def __init__(
        self,
        context: codemod.CodemodContext,
        *,
        modules: Optional[ListChangeSet] = None,
        problematic: Optional[ListChangeSet] = None,
        excluded: Optional[ListChangeSet] = None,
    ):
        super().__init__(context)
        self.modules_changeset = modules
        self.problematic_changeset = problematic
        self.excluded_changeset = excluded

    def iter_transforms(self) -> Iterator[m.MatcherDecoratableVisitor]:
        if self.modules_changeset:
            yield ModifyListElements(change_set=self.modules_changeset, scope_matcher=self.modules_scope)
        if self.problematic_changeset:
            yield ModifyListElements(change_set=self.problematic_changeset, scope_matcher=self.problematic_scope)
        if self.excluded_changeset:
            yield ModifyListElements(change_set=self.excluded_changeset, scope_matcher=self.excluded_scope)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        for transform in self.iter_transforms():
            tree = tree.visit(transform)
        return tree


class LVGLCodemod(codemod.Codemod):
    """Generates createstubs.py LVGL flavor."""

    modules_transform: ModulesUpdateCodemod
    init_node: cst.SimpleStatementLine

    def __init__(
        self,
        context: codemod.CodemodContext,
        modules_transform: Optional[ModulesUpdateCodemod] = None,
        init_node: Optional[cst.SimpleStatementLine] = None,
    ):
        super().__init__(context)
        self.modules_transform = modules_transform or ModulesUpdateCodemod(
            self.context, modules=ListChangeSet.from_strings(add=["io", "lodepng", "rtch", "lvgl"], replace=True)
        )
        self.init_node = init_node or cst.parse_module(_LVGL_MAIN)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        init_transform = SimpleStatementReplace(self.init_node, scope_matcher=m.SimpleStatementLine(body=[_STUBBER_MATCHER]))
        tree = tree.visit(init_transform)
        return self.modules_transform.transform_module(tree)


class LowMemoryCodemod(codemod.Codemod):
    """Generates createstubs.py low-memory flavor."""

    def __init__(self, context: codemod.CodemodContext):
        super().__init__(context)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        doc_transformer = ModuleDocCodemod(self.context, _LOW_MEM_MODULE_DOC)
        read_mods_transformer = ReadModulesCodemod(self.context)
        tree = doc_transformer.transform_module(tree)
        return read_mods_transformer.transform_module(tree)


class CreateStubsCodemod(codemod.Codemod):
    """Generates createstubs.py variant based on provided flavor."""

    flavor: CreateStubsFlavor
    modules_transform: ModulesUpdateCodemod

    def __init__(
        self,
        context: codemod.CodemodContext,
        flavor: CreateStubsFlavor = CreateStubsFlavor.BASE,
        *,
        modules: Optional[ListChangeSet] = None,
        problematic: Optional[ListChangeSet] = None,
        excluded: Optional[ListChangeSet] = None,
    ):
        super().__init__(context)
        self.flavor = flavor
        self.modules_transform = ModulesUpdateCodemod(
            self.context,
            modules=modules,
            problematic=problematic,
            excluded=excluded,
        )

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        mod_flavors = {
            CreateStubsFlavor.LVGL: LVGLCodemod,
            CreateStubsFlavor.LOW_MEM: LowMemoryCodemod,
        }
        if self.flavor in mod_flavors:
            tree = mod_flavors[self.flavor](self.context).transform_module(tree)
        return self.modules_transform.transform_module(tree)
