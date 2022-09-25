from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import libcst as cst


@dataclass
class TypeInfo:
    "contains the  functiondefs and classdefs info read from the stubs source"
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


MODULE_KEY = tuple(["__module"])

# debug helper
_m = cst.parse_module("")


class StubTypingCollector(cst.CSTVisitor):
    def __init__(self):
        # stack for storing the canonical name of the current function
        self.stack: List[str] = []
        # store the annotations
        self.annotations: Dict[
            Tuple[str, ...],  # key: tuple of canonical class/function name
            TypeInfo,  # value: TypeInfo
        ] = {}

    # ------------------------------------------------------------
    def visit_Module(self, node: cst.Module) -> bool:
        "Store the module docstring"
        if node.get_docstring():
            ## TODO: try / catch
            assert isinstance(node.body[0], cst.SimpleStatementLine)
            ti = TypeInfo(
                name="module",
                params=None,
                returns=None,
                docstr_node=node.body[0],
                decorators=(),
                def_type="module",
            )
            self.annotations[MODULE_KEY] = ti
        return True

    # ------------------------------------------------------------
    #  keep track of the the (class, method) names to the stack
    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        "Store the class docstring"
        self.stack.append(node.name.value)
        if node.get_docstring():
            ## TODO: try / catch
            assert isinstance(node.body.body[0], cst.SimpleStatementLine)
            docstr_node = node.body.body[0]
        else:
            docstr_node = None

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
        self.stack.pop()

    # ------------------------------------------------------------
    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        "store each function/method signature"
        self.stack.append(node.name.value)
        if node.get_docstring():
            ## TODO: try / catch
            assert isinstance(node.body.body[0], cst.SimpleStatementLine)
            docstr_node = node.body.body[0]
        else:
            docstr_node = None

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

    def leave_FunctionDef(self, original_node: cst.FunctionDef) -> None:
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
        if src_node:
            return dest_node.with_changes(body=src_node.body)
        else:
            return dest_node

    # just checking
    if not isinstance(dest_node.body, cst.IndentedBlock):
        raise TransformError("Expected Def with Indented body")
    # if not isinstance(dest_node.body.body, Sequence):
    #     # this is likely a .pyi file or a type declaration with a trailing ...
    #     # no changes
    #     return dest_node

    # classdef of functiondef with an indented body
    # need some funcky casting to avoid issues with changing the body
    # note : indented body is nested : body.body
    if dest_node.get_docstring() != None:
        body = tuple([src_comment] + list(dest_node.body.body[1:]))
    else:
        # append the new docstring and append the function body
        body = tuple([src_comment] + list(dest_node.body.body))

    body_2 = dest_node.body.with_changes(body=body)

    return dest_node.with_changes(body=body_2)


def update_module_docstr(node: cst.Module, doc_tree: Optional[cst.SimpleStatementLine]) -> Any:
    "Update the docstring of a module"
    if not doc_tree:
        return node
    # # just checking
    # if not (isinstance(node.body, Sequence)):
    #     raise TransformError("Expected module with body")

    # need some funcky casting to avoid issues with changing the body
    if node.get_docstring() != None:
        body = tuple([doc_tree] + list(node.body[1:]))
    else:
        # append the new docstring and append the function body
        body = tuple([doc_tree] + list(node.body))

    return node.with_changes(body=body)
