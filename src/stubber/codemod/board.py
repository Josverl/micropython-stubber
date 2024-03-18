"""" 
Codemods to create the different variants of createstubs.py
"""

from __future__ import annotations

from enum import Enum
from typing import Iterator, Optional

import libcst as cst
import libcst.codemod as codemod
from libcst import matchers as m
from libcst.codemod._codemod import Codemod  # type: ignore
from packaging.version import Version

from stubber import __version__
from stubber.codemod._partials import Partial
from stubber.codemod.modify_list import ListChangeSet, ModifyListElements
from stubber.cst_transformer import update_module_docstr

# matches on `stubber = Stubber()`
_STUBBER_MATCHER = m.Assign(
    targets=[
        m.AssignTarget(
            target=m.Name("stubber"),
        )
    ],
    value=m.Call(func=m.Name("Stubber")),
)

# matches on `stubber.modules = ["foo","bar"]`
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

# matches on `def main():`
_DEF_MAIN_MATCHER = m.FunctionDef(name=m.Name(value="main"))

# matches on `self.problematic = []`
_PROBLEMATIC_MATCHER = m.Assign(
    targets=[
        m.AssignTarget(
            target=m.Attribute(
                value=m.Name("self"),
                attr=m.Name("problematic"),
            )
        )
    ]
)
# matches on `self.excluded = []`
_EXCLUDED_MATCHER = m.Assign(
    targets=[
        m.AssignTarget(
            target=m.Attribute(
                value=m.Name("self"),
                attr=m.Name("excluded"),
            )
        )
    ]
)


_LOW_MEM_MODULE_DOC = '''
"""Create stubs for (all) modules on a MicroPython board.

    This variant of the createstubs.py script is optimised for use on low-memory devices, and reads the list of modules from a text file 
    `modulelist.txt` in the root or `libs` folder that should be uploaded to the device.
    If that cannot be found then only a single module (micropython) is stubbed.
    In order to run this on low-memory devices two additional steps are recommended: 
    - minifification, using python-minifier
      to reduce overall size, and remove logging overhead.
    - cross compilation, using mpy-cross, 
      to avoid the compilation step on the micropython device 
"""
'''


_DB_MODULE_DOC = '''
"""
Create stubs for (all) modules on a MicroPython board.

    This variant of the createstubs.py script is optimized for use on very-low-memory devices.
    Note: this version has undergone limited testing.
    
    1) reads the list of modules from a text file `modulelist.txt` that should be uploaded to the device.
    2) stored the already processed modules in a text file `modulelist.done` 
    3) process the modules in the database:
        - stub the module
        - update the modulelist.done file
        - reboots the device if it runs out of memory
    4) creates the modules.json

    If that cannot be found then only a single module (micropython) is stubbed.
    In order to run this on low-memory devices two additional steps are recommended: 
    - minification, using python-minifierto reduce overall size, and remove logging overhead.
    - cross compilation, using mpy-cross, to avoid the compilation step on the micropython device 

"""
'''

_LVGL_MODULE_DOC = '''
"""
Create stubs for the lvgl modules on a MicroPython board.

Note that the stubs can be very large, and it may be best to directly store them on an SD card if your device supports this.
"""
'''


class CreateStubsVariant(str, Enum):
    """Dictates create stubs target variant."""

    BASE = "base"
    MEM = "mem"
    DB = "db"
    LVGL = "lvgl"


class ReadModulesCodemod(codemod.Codemod):
    """Replaces static modules list with file-load method."""

    modules_reader_node: cst.Module

    def __init__(self, context: codemod.CodemodContext, reader_node: Optional[cst.Module] = None):
        super().__init__(context)
        self.modules_reader_node = reader_node or cst.parse_module(
            Partial.MODULES_READER.contents(),  # type: ignore
        )

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        """Replaces static modules list with file-load method."""
        repl_node = m.findall(tree, m.SimpleStatementLine(body=[_MODULES_MATCHER]), metadata_resolver=self)
        tree = tree.deep_replace(repl_node[0], self.modules_reader_node)
        return tree


class ModuleDocCodemod(codemod.Codemod):
    """Replaces a module's docstring."""

    module_doc: str

    def __init__(self, context: codemod.CodemodContext, module_doc: str):
        super().__init__(context)
        if module_doc.endswith('"""\n'):
            generated = f'\nThis variant was generated from createstubs.py by micropython-stubber v{Version(__version__).base_version}\n"""\n'
            module_doc = module_doc[:-4] + generated
        self.module_doc = module_doc

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        """Replaces a module's docstring."""
        return update_module_docstr(tree, self.module_doc)


class ModulesUpdateCodemod(codemod.Codemod):
    """Update or replace the static module list(s) with the provided changes."""

    modules_changeset: Optional[ListChangeSet]
    problematic_changeset: Optional[ListChangeSet]
    excluded_changeset: Optional[ListChangeSet]

    modules_scope: m.BaseMatcherNode = _MODULES_MATCHER  # matches on `stubber.modules = ["foo","bar"]`
    problematic_scope: m.BaseMatcherNode = _PROBLEMATIC_MATCHER  # matches on `self.problematic = []`
    excluded_scope: m.BaseMatcherNode = _EXCLUDED_MATCHER  # matches on `self.excluded = []`

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

    def iter_transforms(self) -> Iterator[m.MatcherDecoratableTransformer]:
        if self.modules_changeset:
            yield ModifyListElements(change_set=self.modules_changeset).with_scope(self.modules_scope)  # type: ignore
        if self.problematic_changeset:
            yield ModifyListElements(change_set=self.problematic_changeset).with_scope(self.problematic_scope)  # type: ignore
        if self.excluded_changeset:
            yield ModifyListElements(change_set=self.excluded_changeset).with_scope(self.excluded_scope)  # type: ignore

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        """Update or replace the static module list(s) with the provided changes."""
        for transform in self.iter_transforms():
            tree = tree.visit(transform)
        return tree


class LVGLCodemod(codemod.Codemod):
    """Generates createstubs.py LVGL variant."""

    modules_transform: ModulesUpdateCodemod
    init_node: cst.Module

    def __init__(
        self,
        context: codemod.CodemodContext,
    ):
        super().__init__(context)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        """Generates createstubs.py LVGL variant."""
        # repl_node = m.findall(tree, m.SimpleStatementLine(body=[_STUBBER_MATCHER]), metadata_resolver=self)
        # tree = tree.deep_replace(repl_node[0], self.init_node)
        # return self.modules_transform.transform_module_impl(tree)

        docstr_transformer = ModuleDocCodemod(self.context, _LVGL_MODULE_DOC)
        def_main_tree = cst.parse_module(
            Partial.LVGL_MAIN.contents(),  # type: ignore
        )

        work_tree = docstr_transformer.transform_module_impl(tree)
        matches = m.findall(work_tree, _DEF_MAIN_MATCHER, metadata_resolver=self)

        entry_tree = work_tree.deep_replace(matches[0], def_main_tree)
        return tree.with_deep_changes(tree, body=(*entry_tree.body,))


class LowMemoryCodemod(codemod.Codemod):
    """Generates createstubs.py low-memory variant."""

    def __init__(self, context: codemod.CodemodContext):
        super().__init__(context)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        """
        Generates createstubs.py low-memory variant.
        - replace the static module list with the low-memory variant (read from file)
        """

        docstr_transformer = ModuleDocCodemod(self.context, _LOW_MEM_MODULE_DOC)
        read_mods_transformer = ReadModulesCodemod(self.context)
        # update the docstring
        doc_tree = docstr_transformer.transform_module_impl(tree)
        # load the modules from file
        read_mods_tree = read_mods_transformer.transform_module_impl(doc_tree)
        # apply all changes to the original tree
        return tree.with_deep_changes(tree, body=(*read_mods_tree.body,))


class DBCodemod(codemod.Codemod):
    """Generates createstubs.py db variant."""

    def __init__(self, context: codemod.CodemodContext):
        super().__init__(context)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        """Generates createstubs.py db variant."""
        docstr_transformer = ModuleDocCodemod(self.context, _DB_MODULE_DOC)
        def_main_tree = cst.parse_module(
            Partial.DB_MAIN.contents(),  # type: ignore
        )

        work_tree = docstr_transformer.transform_module_impl(tree)
        matches = m.findall(work_tree, _DEF_MAIN_MATCHER, metadata_resolver=self)

        entry_tree = work_tree.deep_replace(matches[0], def_main_tree)
        return tree.with_deep_changes(tree, body=(*entry_tree.body,))


class CreateStubsCodemod(codemod.Codemod):
    """Generates createstubs.py variant based on provided variant."""

    variant: CreateStubsVariant
    modules_transform: ModulesUpdateCodemod

    def __init__(
        self,
        context: codemod.CodemodContext,
        variant: CreateStubsVariant = CreateStubsVariant.BASE,
        *,
        modules: Optional[ListChangeSet] = None,
        problematic: Optional[ListChangeSet] = None,
        excluded: Optional[ListChangeSet] = None,
    ):
        super().__init__(context)
        self.variant = variant
        self.modules_transform = ModulesUpdateCodemod(
            self.context,
            modules=modules,
            problematic=problematic,
            excluded=excluded,
        )
        self.context.scratch.setdefault("modules_transform", self.modules_transform)

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        """
        Generates a createstubs.py variant based on provided flavor.
        Transform it to emit the appropriate variant of createstubs.py,
        Optionally allows to replace the
        - list of modules to stub. (if relevant for the flavour)
        - list of problematic modules.
        - list of excluded modules.
        """
        mod_variants = {
            CreateStubsVariant.LVGL: LVGLCodemod,
            CreateStubsVariant.MEM: LowMemoryCodemod,
            CreateStubsVariant.DB: DBCodemod,
        }
        if self.variant in mod_variants:
            # get the appropriate codemod for the variant and transform the tree
            codemod = mod_variants[self.variant]
            tree = codemod(self.context).transform_module(tree)
        # update the tree with the list of modules to stub , excluded modules and problematic modules
        tree = self.modules_transform.transform_module(tree)
        return tree
