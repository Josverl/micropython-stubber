"""
Gather all TypeVar and TypeAlias assignments in a module.
"""

from typing import Dict, List, Optional, Sequence, Tuple, Union

import libcst as cst
import libcst.matchers as m
from libcst import SimpleStatementLine
from libcst.codemod._context import CodemodContext
from libcst.codemod._visitor import ContextAwareTransformer, ContextAwareVisitor
from libcst.codemod.visitors._add_imports import _skip_first
from typing_extensions import TypeAlias

from mpflash.logger import log

TypeHelper: TypeAlias = Union[cst.Assign, cst.AnnAssign]
TypeHelpers: TypeAlias = List[TypeHelper]
Statement: TypeAlias = Union[cst.SimpleStatementLine, cst.BaseCompoundStatement]

_mod = cst.parse_module("")  # Debugging aid : _mod.code_for_node(node)
_code = _mod.code_for_node  #     Debugging aid : _code(node)


def is_TypeAlias(statement) -> bool:
    "Annotated Assign -  Foo:TypeAlias = ..."
    if m.matches(statement, m.SimpleStatementLine()):
        statement = statement.body[0]
    return m.matches(
        statement,
        m.AnnAssign(annotation=m.Annotation(annotation=m.Name(value="TypeAlias"))),
    )


def is_TypeVar(statement):
    "Assign - Foo = Typevar(...)"
    if m.matches(statement, m.SimpleStatementLine()):
        statement = statement.body[0]
    return m.matches(
        statement,
        m.Assign(value=m.Call(func=m.Name(value="TypeVar"))),
    )


def is_CONSTANT(statement):
    """
    Assign   -  FOO = ...
    AnnAssign-  FOO:bool = ...
    """

    try:
        if m.matches(statement, m.SimpleStatementLine()):
            statement = statement.body[0]
        if m.matches(statement, m.Assign()):
            if len(statement.targets) != 1:
                return False
            if m.matches(statement.targets[0], m.Name()):
                if statement.targets[0].target.value.isupper():
                    return True
            elif m.matches(statement.targets[0], m.AssignTarget()):
                if m.matches(statement.targets[0].target, m.Name()):
                    if statement.targets[0].children[0].value.isupper():
                        return True
    except Exception as e:
        log.debug(f"Error in is_CONSTANT: {e}")
        return False
    return False


def is_AnnCONSTANT(statement):
    """
    Assign   -  FOO = ...
    AnnAssign-  FOO:bool = ...
    """

    if m.matches(statement, m.SimpleStatementLine()):
        statement = statement.body[0]
    if m.matches(statement, m.AnnAssign()):
        if statement.target.value.isupper():
            return True
    return False


def is_ParamSpec(statement):
    "Assign - Foo = ParamSpec(...)"
    if m.matches(statement, m.SimpleStatementLine()):
        statement = statement.body[0]
    return m.matches(
        statement,
        m.Assign(value=m.Call(func=m.Name(value="ParamSpec"))),
    )


def is_import(statement):
    "import - import foo"
    return m.matches(statement, m.SimpleStatementLine(body=[m.ImportFrom() | m.Import()]))


def is_docstr(statement):
    "single or triple quoted string"
    if m.matches(statement, m.SimpleStatementLine()):
        statement = statement.body[0]
    return m.matches(
        statement,
        m.Expr(value=m.SimpleString()),
        # | m.TripleQuotedString(),
    )


class GatherTypeHelpers(ContextAwareVisitor):
    """
    A class for tracking visited TypeVars and TypeAliases.
    """

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        # Track all of the TypeVar, TypeAlias and Paramspec assignments found
        self.all_typehelpers: Dict[Tuple[str, ...], TypeHelpers] = {}
        self.stack: List[str] = []

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        """keep track of the the (class, method) names to the stack"""
        self.stack.append(node.name.value)

    def leave_ClassDef(self, original_node: cst.ClassDef) -> None:
        """remove the class name from the stack"""
        self.stack.pop()

    def visit_Assign(self, node: cst.Assign) -> None:
        """
        Find all TypeVar assignments in the module.
        format: T = TypeVar("T", int, float, str, bytes, Tuple)
        or Constants
        """
        # is this a TypeVar assignment?
        # needs to be more robust
        if is_TypeVar(node) or is_ParamSpec(node) or is_CONSTANT(node):
            key = tuple(self.stack)
            if not key in self.all_typehelpers:
                self.all_typehelpers[key] = []
            self.all_typehelpers[key].append(node)

    def visit_AnnAssign(self, node: cst.AnnAssign) -> None:
        """ "
        Find all TypeAlias assignments in the module.
        format: T: TypeAlias = str
        """
        if is_TypeAlias(node) or is_AnnCONSTANT(node):
            key = tuple(self.stack)
            if not key in self.all_typehelpers:
                self.all_typehelpers[key] = []
            self.all_typehelpers[key].append(node)


class AddTypeHelpers(ContextAwareTransformer):
    """
    Visitor loosly based on AddImportsVisitor
    """

    CONTEXT_KEY = "AddTypeHelpers"

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        self.new_typehelpers: Dict[Tuple[str, ...], TypeHelpers] = context.scratch.get(self.CONTEXT_KEY, [])
        self.all_typehelpers: Dict[Tuple[str, ...], TypeHelpers] = {}
        self.stack: List[str] = []

    @classmethod
    def add_helpers(cls, context: CodemodContext, helpers: Dict[Tuple[str, ...], TypeHelpers]):
        context.scratch[cls.CONTEXT_KEY] = helpers
        # add the typevar to the module

    @staticmethod
    def skip_first(body: Sequence[cst.BaseStatement]) -> bool:
        # Is there a __strict__ flag or docstring at the top?
        if m.matches(
            body[0],
            m.SimpleStatementLine(body=[m.Assign(targets=[m.AssignTarget(target=m.Name("__strict__"))])])
            | m.SimpleStatementLine(body=[m.Expr(value=m.SimpleString())]),
        ):
            return True
        return False

    def leave_Module(
        self,
        original_node: cst.Module,
        updated_node: cst.Module,
    ) -> cst.Module:
        stack_id = tuple(self.stack)
        if stack_id not in self.new_typehelpers:
            # nothing new to add @ module level
            return updated_node

        # split the body of the module or classdef into 3 parts
        # before and after the insertions point , and a list of the TV and TA statements
        body = self.update_body(updated_node.body, stack_id)
        return updated_node.with_changes(body=body)

    def update_body(self, body: Sequence[cst.BaseStatement], stack_id):
        (
            statements_before,
            helper_statements,
            statements_after,
        ) = self._split_body(body)

        # simpler to compare as text than to compare the nodes -
        existing_targets = [
            helper.body[0].targets[0].target.value  # type: ignore
            for helper in helper_statements
            if is_TypeVar(helper) or is_ParamSpec(helper) or is_CONSTANT(helper)
        ] + [
            helper.body[0].target.value  # type: ignore
            for helper in helper_statements
            if is_TypeAlias(helper) or is_AnnCONSTANT(helper)
        ]
        statements_to_add = []
        for new_typehelper in self.new_typehelpers[stack_id]:
            if isinstance(new_typehelper, cst.AnnAssign):
                if new_typehelper.target.value not in existing_targets:  # type: ignore
                    statements_to_add.append(SimpleStatementLine(body=[new_typehelper]))
            elif isinstance(new_typehelper, cst.Assign):
                if new_typehelper.targets[0].target.value not in existing_targets:  # type: ignore
                    statements_to_add.append(SimpleStatementLine(body=[new_typehelper]))

        body = (
            *statements_before,
            *statements_to_add,
            *statements_after,
        )
        return body

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        """keep track of the the (class, method) names to the stack"""
        self.stack.append(node.name.value)

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        stack_id = tuple(self.stack)
        self.stack.pop()
        if stack_id not in self.new_typehelpers:
            # no changes to the class
            return updated_node
        # split the body of the module or classdef into 3 parts
        if isinstance(updated_node.body, cst.IndentedBlock):
            flat_body = self.update_body(updated_node.body.body, stack_id)
            new_body = cst.IndentedBlock(
                body=flat_body,
                header=updated_node.body.header,
                footer=updated_node.body.footer,
                indent=updated_node.body.indent,
            )
        else:
            flat_body = self.update_body([], stack_id)
            new_body = cst.IndentedBlock(
                body=flat_body,
            )
        return updated_node.with_changes(body=new_body)

    def _split_body(
        self,
        body: Sequence[cst.BaseStatement],
    ) -> Tuple[
        Sequence[cst.BaseStatement],
        Sequence[cst.BaseStatement],
        Sequence[cst.BaseStatement],
    ]:
        """
        Split the module into 3 parts:
        - before any TypeAlias, TypeVar or ParamSpec statements
        - the TypeAlias and TypeVar statements
        - the rest of the module after the TypeAlias and TypeVar statements
        """
        last_import = first_typehelper = last_typehelper = -1
        start = 0
        if self.skip_first(body):
            start = 1

        for i, statement in enumerate(body[start:]):
            if is_import(statement):
                last_import = i + start
                continue
            if (
                is_TypeVar(statement)
                or is_TypeAlias(statement)
                or is_ParamSpec(statement)
                or is_CONSTANT(statement)
                or is_AnnCONSTANT(statement)
                or is_docstr(statement)
            ):
                if first_typehelper == -1:
                    first_typehelper = i + start
                last_typehelper = i + start
        # insert as high as possible, but after the last import and last TypeVar/TypeAlias statement
        insert_after = max(start, last_import + 1, last_typehelper + 1)
        assert insert_after != -1, "insert_after must be != -1"
        #
        before = list(body[:insert_after])
        after = list(body[insert_after:])
        helper_statements: Sequence[cst.SimpleStatementLine] = list(body[first_typehelper : last_typehelper + 1])  # type: ignore
        return (before, helper_statements, after)
