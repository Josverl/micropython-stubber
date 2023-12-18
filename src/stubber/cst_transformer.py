"""helper functions for stub transformations"""

# sourcery skip: snake-case-functions
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import libcst as cst


@dataclass
class TypeInfo:
    "contains the functiondefs and classdefs info read from the stubs source"
    name: str
    decorators: Sequence[cst.Decorator]
    params: Optional[cst.Parameters] = None
    returns: Optional[cst.Annotation] = None
    docstr_node: Optional[cst.SimpleStatementLine] = None
    def_node: Optional[Union[cst.FunctionDef, cst.ClassDef]] = None
    def_type: str = "?"  # funcdef or classdef or module


class TransformError(Exception):
    """
    Error raised upon encountering a known error while attempting to transform
    the tree.
    """


MODULE_KEY = ("__module",)
MODDOC_KEY = ("__module_docstring",)

# debug helper
_m = cst.parse_module("")


class StubTypingCollector(cst.CSTVisitor):
    """
    Collect the function/method and class definitions from the stubs source
    """

    def __init__(self):
        # stack for storing the canonical name of the current function
        self.stack: List[str] = []
        # store the annotations
        self.annotations: Dict[
            Tuple[str, ...],  # key: tuple of canonical class/function name
            Union[TypeInfo, str],
        ] = {}
        self.comments :List[str] = []

    # ------------------------------------------------------------
    def visit_Module(self, node: cst.Module) -> bool:
        """Store the module docstring"""
        docstr = node.get_docstring()
        if docstr:
            self.annotations[MODULE_KEY] = docstr
        return True
    def visit_Comment(self, node: cst.Comment) -> None:
        """
        connect comments from the source
        """
        comment = node.value
        if comment.startswith("# MCU: ") or comment.startswith("# Stubber:"):
            # very basic way to detect the stubber comments that we want to copy over
            self.comments.append(comment)

    # ------------------------------------------------------------
    #  keep track of the the (class, method) names to the stack
    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        """
        collect info from a classdef:
        - name, decorators, docstring
        """
        # "Store the class docstring
        docstr_node = self.update_append_first_node(node)
        ti = TypeInfo(
            name=node.name.value,
            params=None,
            returns=None,
            docstr_node=docstr_node,
            decorators=node.decorators,
            def_type="classdef",
            def_node=node,
        )
        self.annotations[tuple(self.stack)] = ti

    def leave_ClassDef(self, original_node: cst.ClassDef) -> None:
        """remove the class name from the stack"""
        self.stack.pop()

    # ------------------------------------------------------------
    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        """
        collect info from a function/method
        - name, decorators, params, returns, docstring
        """
        # "store each function/method signature"
        docstr_node = self.update_append_first_node(node)
        ti = TypeInfo(
            name=node.name.value,
            params=node.params,
            returns=node.returns,
            docstr_node=docstr_node,
            decorators=node.decorators,
            def_type="funcdef",
            def_node=node,
        )
        self.annotations[tuple(self.stack)] = ti

    def update_append_first_node(self, node):
        """Store the function/method docstring or function/method sig"""
        self.stack.append(node.name.value)
        if node.get_docstring():
            assert isinstance(node.body.body[0], cst.SimpleStatementLine)
            return node.body.body[0]
        else:
            return None

    def leave_FunctionDef(self, original_node: cst.FunctionDef) -> None:
        """remove the function/method name from the stack"""
        self.stack.pop()


def update_def_docstr(
    dest_node: Union[cst.FunctionDef, cst.ClassDef],
    src_comment: Optional[cst.SimpleStatementLine],
    src_node=None,
) -> Any:
    """
    Update the docstring of a function/method or class

    for functiondefs ending in an ellipsis, the entire body needs to be replaced.
    in this case the src_body is mandatory.
    """
    if not src_comment:
        return dest_node

    # function def on a single line ending with an ellipsis (...)
    if isinstance(dest_node.body, cst.SimpleStatementSuite):
        # in order to add a boy the simple hack is to copy the src_node.body
        return dest_node.with_changes(body=src_node.body) if src_node else dest_node
    # just checking
    if not isinstance(dest_node.body, cst.IndentedBlock):
        raise TransformError("Expected Def with Indented body")

    # classdef of functiondef with an indented body
    # need some funcky casting to avoid issues with changing the body
    # note : indented body is nested : body.body
    if dest_node.get_docstring() is None:
        # append the new docstring and append the function body
        body = tuple([src_comment] + list(dest_node.body.body))
    else:
        body = tuple([src_comment] + list(dest_node.body.body[1:]))
    body_2 = dest_node.body.with_changes(body=body)

    return dest_node.with_changes(body=body_2)


def update_module_docstr(
    node: cst.Module,
    doc_tree: Optional[Union[str, cst.SimpleStatementLine, cst.BaseCompoundStatement]],
) -> Any:
    """
    Add or update the docstring of a module
    """
    if not doc_tree:
        return node
    if not isinstance(doc_tree, (str, cst.SimpleStatementLine, cst.BaseCompoundStatement)):  # type: ignore
        raise TransformError("Expected a docstring or a statement")
    if isinstance(doc_tree, str):
        doc_tree = cst.parse_statement(doc_tree)
    # need some funcky casting to avoid issues with changing the body
    if node.get_docstring() is None:
        # append the new docstring and append the function body
        body = tuple([doc_tree] + list(node.body))  # type: ignore
    else:
        body = tuple([doc_tree] + list(node.body[1:]))  # type: ignore
    return node.with_changes(body=body)
