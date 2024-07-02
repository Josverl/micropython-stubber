# sourcery skip: snake-case-functions
"""Merge documentation and type information from from the docstubs into a board stub"""
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor, GatherImportsVisitor, ImportItem
from libcst.helpers.module import insert_header_comments
from mpflash.logger import log

from stubber.cst_transformer import (
    MODULE_KEY,
    StubTypingCollector,
    TypeInfo,
    update_def_docstr,
    update_module_docstr,
)

##########################################################################################
# # log = logging.getLogger(__name__)
#########################################################################################
empty_module = cst.parse_module("")


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
            # "-sf",
            "--stubfile",
            dest="docstub_file",
            metavar="PATH",
            help="The path to the doc-stub file",
            type=str,
            required=True,
        )

    def __init__(self, context: CodemodContext, docstub_file: Union[Path, str]) -> None:
        """initialize the base class with context, and save our args."""
        super().__init__(context)
        self.replace_functiondef_with_classdef = True
        # stack for storing the canonical name of the current function/method
        self.stack: List[str] = []
        # stubfile is the path to the doc-stub file
        self.docstub_path = Path(docstub_file)
        # read the stub file from the path
        self.docstub_source = self.docstub_path.read_text(encoding="utf-8")
        # store the annotations
        self.annotations: Dict[
            Tuple[str, ...],  # key: tuple of canonical class/function name
            Union[TypeInfo, str],  # value: TypeInfo
        ] = {}
        self.comments: List[str] = []

        self.stub_imports: Dict[str, ImportItem] = {}
        self.all_imports: List[Union[cst.Import, cst.ImportFrom]] = []
        # parse the doc-stub file
        if self.docstub_source:
            try:
                # parse the doc-stub file
                stub_tree = cst.parse_module(self.docstub_source)
            except cst.ParserSyntaxError as e:
                log.error(f"Error parsing {self.docstub_path}: {e}")
                raise ValueError(f"Error parsing {self.docstub_path}: {e}") from e
            # create the collectors
            typing_collector = StubTypingCollector()
            import_collector = GatherImportsVisitor(context)
            # visit the doc-stub file with all collectors
            stub_tree.visit(typing_collector)
            self.annotations = typing_collector.annotations
            self.comments = typing_collector.comments
            # Store the imports that were added to the stub file
            stub_tree.visit(import_collector)
            self.stub_imports = import_collector.symbol_mapping
            self.all_imports = import_collector.all_imports

    # ------------------------------------------------------------------------

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        """
        This method is responsible for updating the module node after processing it in the codemod.
        It performs the following tasks:
        1. Adds any needed imports from the doc-stub.
        2. Adds `from module import *` from the doc-stub.
        3. Updates the module docstring.
        4. Updates the comments in the module.

        :param original_node: The original module node.
        :param updated_node: The updated module node after processing.
        :return: The updated module node.
        """
        # --------------------------------------------------------------------
        # add any needed imports from the doc-stub
        for k in self.stub_imports.keys():
            imp = self.stub_imports[k]
            log.trace(f"add: import {k} = {imp}")
            AddImportsVisitor.add_needed_import(
                self.context,
                module=imp.module_name,
                obj=imp.obj_name,
                asname=imp.alias,
                relative=imp.relative,
            )

        # add `from module import *` from the doc-stub
        # FIXME: this cases a problem if there is also a 'from module import foobar' in the firmware stub
        # also all comments get removed from the import
        if self.all_imports:
            for imp in self.all_imports:
                if isinstance(imp, cst.ImportFrom):
                    # perhaps this is an import from *
                    if isinstance(imp.names, cst.ImportStar):
                        # bit of a hack to get the full module name
                        empty_mod = cst.parse_module("")
                        full_module_name = empty_mod.code_for_node(imp.module)  # type: ignore
                        log.trace(f"add: from {full_module_name} import *")
                        AddImportsVisitor.add_needed_import(
                            self.context,
                            module=full_module_name,
                            obj="*",
                        )
        # --------------------------------------------------------------------
        # update the docstring.
        if MODULE_KEY not in self.annotations:
            return updated_node

        # update/replace  module docstrings
        # todo: or should we add / merge the docstrings?
        docstub_docstr = self.annotations[MODULE_KEY]
        assert isinstance(docstub_docstr, str)
        src_docstr = original_node.get_docstring() or ""
        if src_docstr or docstub_docstr:
            if docstub_docstr.strip() != src_docstr.strip():
                if src_docstr:
                    new_docstr = f'"""\n' + docstub_docstr + "\n\n---\n" + src_docstr + '\n"""'
                else:
                    new_docstr = f'"""\n' + docstub_docstr + '\n"""'

                docstr_node = cst.SimpleStatementLine(
                    body=[
                        cst.Expr(
                            value=cst.SimpleString(
                                value=new_docstr,
                            )
                        )
                    ]
                )
                updated_node = update_module_docstr(updated_node, docstr_node)
        # --------------------------------------------------------------------
        # update the comments
        updated_node = insert_header_comments(updated_node, self.comments)

        return updated_node
        # --------------------------------------------------------------------

    # ------------------------------------------------------------

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        """keep track of the the (class, method) names to the stack"""
        self.stack.append(node.name.value)

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        stack_id = tuple(self.stack)
        self.stack.pop()
        if stack_id not in self.annotations:
            # no changes to the class
            return updated_node
        # update the firmware_stub from the doc_stub information
        doc_stub = self.annotations[stack_id]
        assert not isinstance(doc_stub, str)
        # first update the docstring
        updated_node = update_def_docstr(updated_node, doc_stub.docstr_node)
        # Sometimes the MCU stubs and the doc stubs have different types : FunctionDef / ClassDef
        # we need to be carefull not to copy over all the annotations if the types are different
        if doc_stub.def_type == "classdef":
            # Same type, we can copy over all the annotations
            # combine the decorators from the doc-stub and the firmware stub
            new_decorators = []
            if doc_stub.decorators:
                new_decorators.extend(doc_stub.decorators)
            if updated_node.decorators:
                new_decorators.extend(updated_node.decorators)

            return updated_node.with_changes(
                decorators=new_decorators,
                bases=doc_stub.def_node.bases,  # type: ignore
            )
        else:
            # Different type: ClassDef != FuncDef ,
            # for now just return the updated node
            return updated_node

    # ------------------------------------------------------------------------
    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        self.stack.append(node.name.value)
        return True

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> Union[cst.FunctionDef, cst.ClassDef]:
        "Update the function Parameters and return type, decorators and docstring"
        stack_id = tuple(self.stack)
        self.stack.pop()
        if stack_id not in self.annotations:
            # no changes to the function
            return updated_node
        # update the firmware_stub from the doc_stub information
        doc_stub = self.annotations[stack_id]
        assert not isinstance(doc_stub, str)
        # first update the docstring
        updated_node = update_def_docstr(updated_node, doc_stub.docstr_node, doc_stub.def_node)
        # Sometimes the MCU stubs and the doc stubs have different types : FunctionDef / ClassDef
        # we need to be carefull not to copy over all the annotations if the types are different
        if doc_stub.def_type == "funcdef":
            # Same type, we can copy over the annotations
            # params that should  not be overwritten by the doc-stub ?
            params_txt = empty_module.code_for_node(original_node.params)
            overwrite_params = params_txt in [
                "",
                "...",
                "*args, **kwargs",
                "self",
                "self, *args, **kwargs",
            ]
            # return that should not be overwritten by the doc-stub ?
            overwrite_return = True
            if original_node.returns:
                try:
                    overwrite_return = original_node.returns.annotation.value in [  # type: ignore
                        "Incomplete",
                        "Any",
                        "...",
                    ]
                except AttributeError:
                    pass
            # combine the decorators from the doc-stub and the firmware stub
            new_decorators = []
            if doc_stub.decorators:
                new_decorators.extend(doc_stub.decorators)
            if updated_node.decorators:
                new_decorators.extend(updated_node.decorators)

            return updated_node.with_changes(
                decorators=new_decorators,
                params=doc_stub.params if overwrite_params else updated_node.params,
                returns=doc_stub.returns if overwrite_return else updated_node.returns,
            )

        elif doc_stub.def_type == "classdef":
            # Different type: ClassDef != FuncDef ,
            if doc_stub.def_node and self.replace_functiondef_with_classdef:
                # replace the functiondef with the classdef from the stub file
                return doc_stub.def_node
            # for now just return the updated node
            return updated_node
        else:
            #  just return the updated node
            return updated_node
