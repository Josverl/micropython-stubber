"""helper functions for stub transformations"""

# sourcery skip: snake-case-functions
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import libcst as cst
from libcst import matchers as m


@dataclass
class TypeInfo:
    "contains the functionDefs and classDefs info read from the stubs source"
    name: str
    decorators: Sequence[cst.Decorator]
    params: Optional[cst.Parameters] = None
    returns: Optional[cst.Annotation] = None
    docstr_node: Optional[cst.SimpleStatementLine] = None
    def_node: Optional[Union[cst.FunctionDef, cst.ClassDef]] = None
    def_type: str = "?"  # funcDef or classDef or module


@dataclass
class AnnoValue:
    "The different values for the annotations"
    docstring: Optional[str] = ""  # strings
    "Module docstring or function/method docstring"
    docstring_node: Optional[cst.SimpleStatementLine] = None
    "the docstring node for a function method to reuse with overloads"
    type_info: Optional[TypeInfo] = None  # simple type
    "function/method or class definition read from the docstub source"
    overloads: List[TypeInfo] = field(default_factory=list)
    "function / method overloads read from the docstub source"
    mp_available: List[TypeInfo] = field(default_factory=list)
    "function / method `overloads` read from the docstub source"
    literal_docstrings: Dict[str, cst.SimpleStatementLine] = field(default_factory=dict)
    "literal/constant name -> docstring node mappings for literal docstrings"


class TransformError(Exception):
    """
    Error raised upon encountering a known error while attempting to transform
    the tree.
    """


MODULE_KEY = ("__module",)
MOD_DOCSTR_KEY = ("__module_docstring",)

# debug helper
_code = cst.parse_module("").code_for_node


def is_property(node: cst.FunctionDef) -> bool:
    """check if the function is a property"""
    return any(m.matches(dec, m.Decorator(decorator=m.Name(value="property"))) for dec in node.decorators)


# FIXME : this is a clumsy way - but I cant find a working matcher for this
def is_setter(node: cst.FunctionDef) -> bool:
    """check if the function is a setter"""
    return any(d for d in _code(node).split("\n") if d.startswith("@") and d.endswith(".setter"))


def is_getter(node: cst.FunctionDef) -> bool:
    """check if the function is a getter"""
    return any(d for d in _code(node).split("\n") if d.startswith("@") and d.endswith(".getter"))


def is_deleter(node: cst.FunctionDef) -> bool:
    """check if the function is a deleter"""
    return any(d for d in _code(node).split("\n") if d.startswith("@") and d.endswith(".deleter"))


class StubTypingCollector(cst.CSTVisitor):
    """
    Collect the function/method and class definitions from ta rich .py or .pyi source
    """

    def __init__(self):
        # stack for storing the canonical name of the current function
        self.stack: List[str] = []
        # store the annotations
        self.annotations: Dict[
            Tuple[str, ...],  # key: tuple of canonical class/function name
            AnnoValue,  # The TypeInfo or list of TypeInfo
        ] = {}
        self.comments: List[str] = []

    def _collect_literal_docstrings(self, body: Sequence[cst.BaseStatement]) -> Dict[str, cst.SimpleStatementLine]:
        """
        Collect literal docstrings from a sequence of statements.
        Looks for patterns like:
        CONSTANT = value
        '''docstring for constant'''
        """
        literal_docstrings = {}

        for i, stmt in enumerate(body):
            # Look for assignment statements
            if isinstance(stmt, cst.SimpleStatementLine) and len(stmt.body) == 1:
                if isinstance(stmt.body[0], (cst.Assign, cst.AnnAssign)):
                    # Get the literal name
                    literal_name = None
                    if isinstance(stmt.body[0], cst.Assign):
                        # Handle regular assignment: CONST = value
                        targets = stmt.body[0].targets
                        if len(targets) == 1 and isinstance(targets[0].target, cst.Name):
                            literal_name = targets[0].target.value
                    elif isinstance(stmt.body[0], cst.AnnAssign):
                        # Handle annotated assignment: CONST: int = value
                        if isinstance(stmt.body[0].target, cst.Name):
                            literal_name = stmt.body[0].target.value

                    # Check if the next statement is a docstring
                    if literal_name and i + 1 < len(body):
                        next_stmt = body[i + 1]
                        if (
                            isinstance(next_stmt, cst.SimpleStatementLine)
                            and len(next_stmt.body) == 1
                            and isinstance(next_stmt.body[0], cst.Expr)
                            and isinstance(next_stmt.body[0].value, cst.SimpleString)
                        ):
                            # Found a literal with a following docstring
                            literal_docstrings[literal_name] = next_stmt

        return literal_docstrings

    # ------------------------------------------------------------
    def visit_Module(self, node: cst.Module) -> bool:
        """Store the module docstring and collect literal docstrings"""
        # Store module docstring
        docstr = node.get_docstring()
        if docstr:
            self.annotations[MODULE_KEY] = AnnoValue(docstring=docstr)

        # Collect module-level literal docstrings
        literal_docstrings = self._collect_literal_docstrings(node.body)
        if literal_docstrings:
            if MODULE_KEY not in self.annotations:
                self.annotations[MODULE_KEY] = AnnoValue()
            self.annotations[MODULE_KEY].literal_docstrings.update(literal_docstrings)

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
        - class-level literal docstrings
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

        # Collect class-level literal docstrings
        literal_docstrings = {}
        if isinstance(node.body, cst.IndentedBlock):
            literal_docstrings = self._collect_literal_docstrings(node.body.body)

        anno_value = AnnoValue(type_info=ti)
        if literal_docstrings:
            anno_value.literal_docstrings.update(literal_docstrings)

        self.annotations[tuple(self.stack)] = anno_value

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
        if is_getter(node):
            extra = ["getter"]
        elif is_setter(node):
            extra = ["setter"]
        elif is_deleter(node):
            extra = ["deleter"]
        else:
            extra = []
        key = tuple(self.stack + extra)

        if not key in self.annotations:
            # store the first function/method signature
            self.annotations[key] = AnnoValue(type_info=ti)

        # save the overload decos (simple name only)
        if any(m.matches(dec, m.Decorator(decorator=m.Name("overload"))) for dec in node.decorators):
            self.annotations[key].overloads.append(ti)
        # save the mp_available decos in any of these forms: Name/Call/Attribute/Call(Attribute)
        if any(
            m.matches(
                dec,
                m.Decorator(
                    decorator=m.OneOf(
                        m.Name("mp_available"),
                        m.Call(func=m.Name("mp_available")),
                        m.Attribute(value=m.DoNotCare(), attr=m.Name("mp_available")),
                        m.Call(func=m.Attribute(value=m.DoNotCare(), attr=m.Name("mp_available"))),
                    )
                ),
            )
            for dec in node.decorators
        ):
            self.annotations[key].mp_available.append(ti)

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
    src_docstr: Optional[Union[cst.SimpleStatementLine, str]] = None,
    src_node=None,
) -> Any:
    """
    Update the docstring of a function/method or class
    The supplied `src_docstr` can be a string or a SimpleStatementLine

    for function defs ending in an ellipsis, the entire body needs to be replaced.
    in this case `src_node` is required.
    """
    if not src_docstr:
        return dest_node
    if isinstance(src_docstr, str):
        if not src_docstr[0] in ('"', "'"):
            src_docstr = f'"""{src_docstr}"""'
        # convert the string to a SimpleStatementLine
        src_docstr = cst.SimpleStatementLine(
            body=[
                cst.Expr(
                    value=cst.SimpleString(
                        value=src_docstr,
                    ),
                ),
            ]
        )

    # function def on a single line ending with an ellipsis (...)
    if isinstance(dest_node.body, cst.SimpleStatementSuite):
        # in order to add a boy the simple hack is to copy the src_node.body
        return dest_node.with_changes(body=src_node.body) if src_node else dest_node
    # just checking
    if not isinstance(dest_node.body, cst.IndentedBlock):
        raise TransformError("Expected Def with Indented body")

    # classdef of functiondef with an indented body
    # need some funky casting to avoid issues with changing the body
    # note : indented body is nested : IndentedBlock.body.body
    if dest_node.get_docstring() is None:
        # append the new docstring and append the function body
        body = tuple([src_docstr] + list(dest_node.body.body))
    else:
        body = tuple([src_docstr] + list(dest_node.body.body[1:]))
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
