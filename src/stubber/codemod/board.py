from __future__ import annotations

from enum import Enum
from typing import Optional, Iterator

import libcst as cst
import libcst.codemod as codemod
from libcst import matchers as m

from stubber.codemod.modify_list import ModifyListElements, ListChangeSet
from stubber.codemod.utils import ScopeableMatcherTransformer
from stubber.cst_transformer import update_module_docstr

from ._partials import Partial

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

_ENTRY_MATCHER = m.FunctionDef(name=m.Name(value="main"))

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


_DB_MODULE_DOC = '''
"""
Create stubs for (all) modules on a MicroPython board.

    This variant of the createstubs.py script is optimized for use on very-low-memory devices.
    Note: this version has undergone limited testing.
    
    1) reads the list of modules from a text file `./modulelist.txt` that should be uploaded to the device.
    2) stored the already processed modules in a text file `./modulelist.done` 
    3) process the modules in the database:
        - stub the module
        - update the modulelist.done file
        - reboots the device if it runs out of memory
    4) creates the modules.json

    If that cannot be found then only a single module (micropython) is stubbed.
    In order to run this on low-memory devices two additional steps are recommended: 
    - minification, using python-minifierto reduce overall size, and remove logging overhead.
    - cross compilation, using mpy-cross, to avoid the compilation step on the micropython device 

You should find a cross-compiled version located here: `./minified/createstubs_db.mpy

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
finally:
    stubber = Stubber(firmware_id=fw_id)
"""


class CreateStubsFlavor(str, Enum):
    """Dictates create stubs target variant."""

    BASE = "base"
    LOW_MEM = "low_mem"
    DB = "db"
    LVGL = "lvgl"


class ReadModulesCodemod(codemod.Codemod):
    """Replaces static modules list with file-load method."""

    modules_reader_node: cst.Module

    def __init__(self, context: codemod.CodemodContext, reader_node: Optional[cst.Module] = None):
        super().__init__(context)
        self.modules_reader_node = reader_node or cst.parse_module(_MODULES_READER)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        repl_node = m.findall(tree, m.SimpleStatementLine(body=[_MODULES_MATCHER]), metadata_resolver=self)
        tree = tree.deep_replace(repl_node[0], self.modules_reader_node)
        return tree


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

    modules_changeset: Optional[ListChangeSet]
    problematic_changeset: Optional[ListChangeSet]
    excluded_changeset: Optional[ListChangeSet]

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

    def iter_transforms(self) -> Iterator[ScopeableMatcherTransformer]:
        if self.modules_changeset:
            yield ModifyListElements(change_set=self.modules_changeset).with_scope(self.modules_scope)
        if self.problematic_changeset:
            yield ModifyListElements(change_set=self.problematic_changeset).with_scope(self.problematic_scope)
        if self.excluded_changeset:
            yield ModifyListElements(change_set=self.excluded_changeset).with_scope(self.excluded_scope)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        for transform in self.iter_transforms():
            tree = tree.visit(transform)
        return tree


class LVGLCodemod(codemod.Codemod):
    """Generates createstubs.py LVGL flavor."""

    modules_transform: ModulesUpdateCodemod
    init_node: cst.Module

    def __init__(
        self,
        context: codemod.CodemodContext,
        modules_transform: Optional[ModulesUpdateCodemod] = None,
        init_node: Optional[cst.Module] = None,
    ):
        super().__init__(context)
        modules_transform = modules_transform or self.context.scratch.get("modules_transform")
        if modules_transform and not isinstance(modules_transform, ModulesUpdateCodemod):
            raise TypeError(f"modules_transform must be of type ModulesUpdateCodemod, received: {type(modules_transform)}")
        self.modules_transform = (
            modules_transform
            if modules_transform and modules_transform.modules_changeset
            else ModulesUpdateCodemod(self.context, modules=ListChangeSet.from_strings(add=["io", "lodepng", "rtch", "lvgl"], replace=True))
        )
        self.init_node = init_node or cst.parse_module(_LVGL_MAIN)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        repl_node = m.findall(tree, m.SimpleStatementLine(body=[_STUBBER_MATCHER]), metadata_resolver=self)
        tree = tree.deep_replace(repl_node[0], self.init_node)
        return self.modules_transform.transform_module_impl(tree)


class LowMemoryCodemod(codemod.Codemod):
    """Generates createstubs.py low-memory flavor."""

    def __init__(self, context: codemod.CodemodContext):
        super().__init__(context)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        doc_transformer = ModuleDocCodemod(self.context, _LOW_MEM_MODULE_DOC)
        read_mods_transformer = ReadModulesCodemod(self.context)
        doc_tree = doc_transformer.transform_module_impl(tree)
        read_mods_tree = read_mods_transformer.transform_module_impl(doc_tree)
        return tree.with_deep_changes(tree, body=(*read_mods_tree.body,))


class DBCodemod(codemod.Codemod):
    """Generates createstubs.py db flavor."""

    def __init__(self, context: codemod.CodemodContext):
        super().__init__(context)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        doc_transformer = ModuleDocCodemod(self.context, _DB_MODULE_DOC)
        entry_module = cst.parse_module(Partial.DB_ENTRY.contents())
        doc_tree = doc_transformer.transform_module_impl(tree)
        entry = m.findall(doc_tree, _ENTRY_MATCHER, metadata_resolver=self)
        entry_tree = doc_tree.deep_replace(entry[0], entry_module)
        return tree.with_deep_changes(tree, body=(*entry_tree.body,))


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
        self.context.scratch.setdefault("modules_transform", self.modules_transform)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        mod_flavors = {
            CreateStubsFlavor.LVGL: LVGLCodemod,
            CreateStubsFlavor.LOW_MEM: LowMemoryCodemod,
            CreateStubsFlavor.DB: DBCodemod,
        }
        tree = self.modules_transform.transform_module(tree)
        if self.flavor in mod_flavors:
            tree = mod_flavors[self.flavor](self.context).transform_module(tree)
        return tree
