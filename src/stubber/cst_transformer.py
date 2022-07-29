from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Set, Tuple, Dict, Union

import libcst as cst
from libcst import matchers as m


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


class TypingCollector(cst.CSTVisitor):
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
        )
        self.annotations[tuple(self.stack)] = ti

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
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
        )
        self.annotations[tuple(self.stack)] = ti

    def leave_FunctionDef(self, node: cst.FunctionDef) -> None:
        self.stack.pop()


class StubMergeTransformer(cst.CSTTransformer):
    """
    A libcst transformer that merges the type-rich information from a doc-stub into
    a firmware stub.
    The resulting file will contain information from both sources.

    - module docstring - from source

    - function parameters and types - from docstubs
    - function return types - from docstubs
    - function docstrings - from source

    """

    def __init__(self, stub: Optional[str] = None) -> None:
        # stack for storing the canonical name of the current function/method
        self.stack: List[str] = []
        # store the annotations
        self.annotations: Dict[
            Tuple[str, ...],  # key: tuple of canonical class/function name
            TypeInfo,  # value: TypeInfo
        ] = {}
        if stub:
            stub_tree = cst.parse_module(stub)
            visitor = TypingCollector()
            stub_tree.visit(visitor)
            self.annotations = visitor.annotations

    # ------------------------------------------------------------------------

    def leave_Module(self, node: cst.Module, updated_node: cst.Module) -> cst.Module:
        "Update the Module docstring"
        if not MODULE_KEY in self.annotations:
            # no changes
            return updated_node

        # todo: merge module docstrings
        new = self.annotations[MODULE_KEY]
        # first update the docstring
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


def update_def_docstr(node: Union[cst.FunctionDef, cst.ClassDef], doc_tree: Optional[cst.SimpleStatementLine]) -> Any:
    "Update the docstring of a function/method or class"
    if not doc_tree:
        return node
    # just checking
    if not (isinstance(node.body, cst.IndentedBlock) and isinstance(node.body.body, Sequence)):
        raise TransformError("Expected Def with Indented body")

    # need some funcky casting to avoid issues with changing the body
    # note : indented body is nested : body.body
    if node.get_docstring():
        body = tuple([doc_tree] + list(node.body.body[1:]))
    else:
        # append the new docstring and append the function body
        body = tuple([doc_tree] + list(node.body.body))

    body_2 = node.body.with_changes(body=body)

    return node.with_changes(body=body_2)


def update_module_docstr(node: cst.Module, doc_tree: Optional[cst.SimpleStatementLine]) -> Any:
    "Update the docstring of a module"
    if not doc_tree:
        return node
    # just checking
    if not (isinstance(node.body, Sequence)):
        raise TransformError("Expected module with body")

    # need some funcky casting to avoid issues with changing the body
    if node.get_docstring():
        body = tuple([doc_tree] + list(node.body[1:]))
    else:
        # append the new docstring and append the function body
        body = tuple([doc_tree] + list(node.body))

    return node.with_changes(body=body)