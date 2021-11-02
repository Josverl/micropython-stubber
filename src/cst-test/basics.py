# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
# relative import Only needed if LibCTS module is not installed
# import sys
# sys.path.append("../../")

from typing import List, Tuple, Dict, Optional, Pattern, Sequence, Union
import libcst as cst
from libcst import (
    SimpleStatementLine,
    BaseCompoundStatement,
    BaseSuite,
    Expr,
    SimpleString,
    ConcatenatedString,
)

from samples import rich_source, simple_stub


class TypingCollector(cst.CSTVisitor):
    def __init__(self):
        # stack for storing the canonical name of the current function def
        self.stack: List[str] = []
        # store the annotations
        self.annotations: Dict[
            Tuple[str, ...],  # key: tuple of canonical class/function name
            Tuple[
                Optional[cst.Parameters],  # Params
                Optional[cst.Annotation],  # returns
                Optional[Sequence[cst.Arg]],  # Class bases
                Optional[str],  # Docstring
            ],  # value: (params, returns, bases, docstring)
        ] = {}

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        # found class def in the source
        # stack +=  [name]
        # annotations+=  [gramps.parent.name], base classes, None,  docstring
        self.stack.append(node.name.value)
        docstring = node.get_docstring(clean=False)
        ##todo: or possible use deep_clone op copy tree
        # classDef>body>identedblock>body>SimpleStatementLine>SimpleString
        bases = node.bases
        key: Tuple[str, ...] = tuple(self.stack)
        self.annotations[key] = (None, None, bases, docstring)
        print(tuple(self.stack))

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        self.stack.pop()

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        self.stack.append(node.name.value)
        docstring = node.get_docstring(clean=False)
        self.annotations[tuple(self.stack)] = (node.params, node.returns, None, docstring)
        return False  # pyi files don't support inner functions, return False to stop the traversal.

    def leave_FunctionDef(self, node: cst.FunctionDef) -> None:
        self.stack.pop()


class TypingTransformer(cst.CSTTransformer):
    # The transformer takes a dict of annotations as input,
    # and applies them to a destination tree

    def __init__(self, annotations):
        # default to overwrite
        self.overwrite_existing_annotations = True
        # stack for storing the canonical name of the current function
        self.stack: List[str] = []
        # store the annotations that are passed in to the transformer
        self.annotations: Dict[
            Tuple[str, ...],  # key: tuple of canonical class/function name
            Tuple[
                Optional[cst.Parameters],  # Params
                Optional[cst.Annotation],  # returns
                Optional[Sequence[cst.Arg]],  # Class bases
                Optional[str],  # Docstring
            ],  # value: (params, returns, bases, docstring)
        ] = annotations

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        self.stack.append(node.name.value)

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.CSTNode:
        key = tuple(self.stack)
        self.stack.pop()
        if key in self.annotations:
            annotations = self.annotations[key]
            # # Todo: P1 add/update docstring
            # print(original_node.body.body[0].body[0].value.value)
            # docstring = cst.SimpleString('""" docstring """')
            return updated_node.with_changes(
                # add/update base class(es)
                bases=annotations[2]
            )
            # Todo: add/update decorators

        return updated_node

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        self.stack.append(node.name.value)
        return False  # pyi files don't support inner functions, return False to stop the traversal.
        # jv: dit kan/mag geloof ik niet in een codemod

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.CSTNode:
        key = tuple(self.stack)
        self.stack.pop()

        if key in self.annotations:

            annotations = self.annotations[key]
            # Todo: add/update Docstring
            return updated_node.with_changes(params=annotations[0], returns=annotations[1])
        return updated_node

        # .ApplyTypeAnnotationsVisitor
        # See https://libcst.readthedocs.io/en/latest/codemods.html#libcst.codemod.visitors.ApplyTypeAnnotationsVisitor
        # more selective example in :  _apply_type_annotations
        # https://libcst.readthedocs.io/en/latest/_modules/libcst/codemod/visitors/_apply_type_annotations.html#ApplyTypeAnnotationsVisitor
        # # Only add new annotation if explicitly told to overwrite existing
        # # annotations or if one doesn't already exist.
        # if self.overwrite_existing_annotations or not updated_node.returns:
        #     updated_node = updated_node.with_changes(
        #         returns=function_annotation.returns
        #     )
        # # Don't override default values when annotating functions
        # new_parameters = self._update_parameters(function_annotation, updated_node)
        # return updated_node.with_changes(params=new_parameters)


# %%


# %%
source_tree = cst.parse_module(simple_stub)
info_tree = cst.parse_module(rich_source)


# %%
visitor = TypingCollector()
info_tree.visit(visitor)

# %%
transformer = TypingTransformer(visitor.annotations)
modified_tree = source_tree.visit(transformer)


# %%
print("=" * 20)
print(modified_tree.code)


# %%
# Use difflib to show the changes to verify type annotations were added as expected.
import difflib

print(
    "".join(difflib.unified_diff(simple_stub.splitlines(True), modified_tree.code.splitlines(True)))
)


# %%
if not modified_tree.deep_equals(source_tree):
    ...  # write to file

# %%
