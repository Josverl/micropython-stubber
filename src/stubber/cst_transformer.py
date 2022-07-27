from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Set, Tuple, Dict

import libcst as cst
from libcst import matchers as m


@dataclass
class TypeInfo:
    "contains the  functiondefs and classdefs info read from the stubs source"
    name: str
    decorators: Sequence[cst.Decorator]
    params: Optional[cst.Parameters] = None
    returns: Optional[cst.Annotation] = None
    docstring: Optional[str] = None


class TransformError(Exception):
    """
    Error raised upon encountering a known error while attempting to transform
    the tree.
    """


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
    #  keep track of the the (class, method) names to the stack
    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        self.stack.append(node.name.value)

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        self.stack.pop()

    # ------------------------------------------------------------
    def visit_Module(self, node: cst.Module) -> bool:
        "Store the module docstring"
        ti = TypeInfo(
            name="module",
            params=None,
            returns=None,
            docstring=node.get_docstring(clean=False),
            decorators=(),
        )
        self.annotations[tuple(["__module"])] = ti
        return True

    # ------------------------------------------------------------
    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        "store each function/method signature"
        self.stack.append(node.name.value)
        ti = TypeInfo(
            name=node.name.value,
            params=node.params,
            returns=node.returns,
            docstring=node.get_docstring(clean=False),
            decorators=node.decorators,
        )
        self.annotations[tuple(self.stack)] = ti
        # pyi files don't support inner functions, return False to stop the traversal.
        return False

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

        # todo: merge module docstrings
        new_body = updated_node.body
        return updated_node.with_changes(body=new_body)

    # ------------------------------------------------------------
    #  keep track of the the (class, method) names to the stack
    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        self.stack.append(node.name.value)

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        self.stack.pop()

    # ------------------------------------------------------------------------
    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        self.stack.append(node.name.value)
        return True

    def leave_FunctionDef(self, node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:

        # fake reading the stub information
        #  x = cst.parse_statement("def foo(pin: int, /, limit: int = 100) -> str: ...")  # type: ignore

        stack_id = tuple(self.stack)
        self.stack.pop()
        if not stack_id in self.annotations:
            return updated_node
        else:

            # update the firmware stub from the source
            new = self.annotations[stack_id]

            # TODO BODY MERGING
            new_body = updated_node.body

            return updated_node.with_changes(
                params=new.params,
                returns=new.returns,
                body=new_body,
                decorators=new.decorators,
            )
