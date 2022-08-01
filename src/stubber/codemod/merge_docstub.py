# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
import argparse
from ast import alias
from pathlib import Path
from typing import List
from libcst import Module
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand


from stubber.cst_transformer import StubTypingCollector, update_def_docstr, update_module_docstr

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple, Dict

import libcst as cst
from libcst.codemod.visitors import AddImportsVisitor, GatherImportsVisitor, RemoveImportsVisitor, ImportItem

from libcst.codemod.visitors._apply_type_annotations import _get_imported_names


@dataclass
class TypeInfo:
    "contains the  functiondefs and classdefs info read from the stubs source"
    name: str
    decorators: Sequence[cst.Decorator]
    params: Optional[cst.Parameters] = None
    returns: Optional[cst.Annotation] = None
    docstr_node: Optional[cst.SimpleStatementLine] = None


class TransformError(Exception):
    """
    Error raised upon encountering a known error while attempting to transform
    the tree.
    """


MODULE_KEY = tuple(["__module"])


class MergeCommand(VisitorBasedCodemodCommand):
    """
    A libcst transformer that merges the type-rich information from a doc-stub into
    a firmware stub.
    The resulting file will contain information from both sources.

    - module docstring - from source

    - function parameters and types - from docstubs
    - function return types - from docstubs
    - function docstrings - from source

    """

    DESCRIPTION: str = "Merge the type-rich information from a doc-stub into a firmware stub"

    @staticmethod
    def add_args(arg_parser: argparse.ArgumentParser) -> None:
        """Add command-line args that a user can specify for running this codemod."""

        arg_parser.add_argument(
            "-sf",
            "--stubfile",
            dest="stub_file",
            metavar="COMMENT",
            help="The path to the doc-stub file",
            type=str,
            required=True,
        )

    def __init__(self, context: CodemodContext, stub_file: str) -> None:
        super().__init__(context)
        # stack for storing the canonical name of the current function/method
        self.stack: List[str] = []
        # stubfile is the path to the doc-stub file
        self.stub_path = Path(stub_file)
        # read the stub file from the path
        self.stub_source = self.stub_path.read_text()
        # store the annotations
        self.annotations: Dict[
            Tuple[str, ...],  # key: tuple of canonical class/function name
            TypeInfo,  # value: TypeInfo
        ] = {}

        self.stub_imports: Dict[str, ImportItem] = {}
        # parse the doc-stub file
        if self.stub_source:
            # parse the doc-stub file
            stub_tree = cst.parse_module(self.stub_source)
            # create the collectors
            typing_collector = StubTypingCollector()
            import_collector = GatherImportsVisitor(context)
            # visit the doc-stub file with all collectors
            stub_tree.visit(typing_collector)
            self.annotations = typing_collector.annotations

            # Store the imports that were added to the stub file
            stub_tree.visit(import_collector)
            self.stub_imports = import_collector.symbol_mapping

    # def transform_module_impl(self, tree: Module) -> Module:
    #     # Return the tree as-is, with absolutely no modification
    #     print(f"hello from {self.DESCRIPTION}")
    #     return tree

    # ------------------------------------------------------------------------

    def leave_Module(self, node: cst.Module, updated_node: cst.Module) -> cst.Module:
        "Update the Module docstring"
        # add any needed imports from the doc-stub
        for k in self.stub_imports.keys():
            _imp = self.stub_imports[k]
            print(f"import {k} = {_imp}")
            AddImportsVisitor.add_needed_import(
                self.context,
                module=_imp.module_name,
                obj=_imp.obj_name,
                asname=_imp.alias,
                relative=_imp.relative,
            )

        # update the docstring.
        if not MODULE_KEY in self.annotations:
            # no changes
            return updated_node

        # update/replace  module docstrings
        # todo: or should we add / merge the docstrings?
        new = self.annotations[MODULE_KEY]

        return update_module_docstr(updated_node, new.docstr_node)

    # ------------------------------------------------------------
    #  keep track of the the (class, method) names to the stack
    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        self.stack.append(node.name.value)

    def leave_ClassDef(self, node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        stack_id = tuple(self.stack)
        self.stack.pop()
        if not stack_id in self.annotations:
            # no changes to the function
            return updated_node
        # update the firmware_stub from the doc_stub information
        new = self.annotations[stack_id]
        # first update the docstring
        updated_node = update_def_docstr(updated_node, new.docstr_node)
        # then any other information
        return updated_node.with_changes(decorators=new.decorators)

    # ------------------------------------------------------------------------
    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        self.stack.append(node.name.value)
        return True

    def leave_FunctionDef(self, node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        "Update the function Parameters and return type, decorators and docstring"

        stack_id = tuple(self.stack)
        self.stack.pop()
        if not stack_id in self.annotations:
            # no changes to the function
            return updated_node
        # update the firmware_stub from the doc_stub information
        new = self.annotations[stack_id]

        # first update the docstring
        updated_node = update_def_docstr(updated_node, new.docstr_node)
        # then any other information
        return updated_node.with_changes(
            params=new.params,
            returns=new.returns,
            decorators=new.decorators,
        )
