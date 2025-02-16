"""
Gather all TypeVar and TypeAlias assignments in a module.
"""

from functools import lru_cache
from typing import List, Sequence, Tuple, Union

import libcst
import libcst.matchers as m
from libcst import SimpleStatementLine
from libcst.codemod._context import CodemodContext
from libcst.codemod._visitor import ContextAwareTransformer, ContextAwareVisitor
from libcst.codemod.visitors._add_imports import _skip_first
from typing_extensions import TypeAlias

# from mpflash.logger import log

TypeHelper: TypeAlias = Union[libcst.Assign, libcst.AnnAssign]
TypeHelpers: TypeAlias = List[TypeHelper]
Statement: TypeAlias = Union[libcst.SimpleStatementLine, libcst.BaseCompoundStatement]

_mod = libcst.parse_module("")  # Debugging aid : _mod.code_for_node(node)
_code = _mod.code_for_node  # Debugging aid : _code(node)


@lru_cache(maxsize=None)
def is_TypeAlias(statement) -> bool:
    "Annotated Assign -  Foo:TypeAlias = ..."
    if m.matches(statement, m.SimpleStatementLine()):
        statement = statement.body[0]
    return m.matches(
        statement,
        m.AnnAssign(annotation=m.Annotation(annotation=m.Name(value="TypeAlias"))),
    )


@lru_cache(maxsize=None)
def is_TypeVar(statement):
    "Assing - Foo = Typevar(...)"
    if m.matches(statement, m.SimpleStatementLine()):
        statement = statement.body[0]
    return m.matches(
        statement,
        m.Assign(value=m.Call(func=m.Name(value="TypeVar"))),
    )


@lru_cache(maxsize=None)
def is_ParamSpec(statement):
    "Assign - Foo = ParamSpec(...)"
    if m.matches(statement, m.SimpleStatementLine()):
        statement = statement.body[0]
    return m.matches(
        statement,
        m.Assign(value=m.Call(func=m.Name(value="ParamSpec"))),
    )


@lru_cache(maxsize=None)
def is_import(statement):
    "import - import foo"
    return m.matches(statement, m.SimpleStatementLine(body=[m.ImportFrom() | m.Import()]))


class GatherTypeHelpers(ContextAwareVisitor):
    """
    A class for tracking visited TypeVars and TypeAliases.
    """

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        # Track all of the TypeVar, TypeAlias and Paramspec assignments found
        self.all_typehelpers: TypeHelpers = []

    def visit_Assign(self, node: libcst.Assign) -> None:
        """
        Find all TypeVar assignments in the module.
        format: T = TypeVar("T", int, float, str, bytes, Tuple)
        """
        # is this a TypeVar assignment?
        # needs to be more robust
        if is_TypeVar(node) or is_ParamSpec(node):
            self.all_typehelpers.append(node)

    def visit_AnnAssign(self, node: libcst.AnnAssign) -> None:
        """ "
        Find all TypeAlias assignments in the module.
        format: T: TypeAlias = str
        """
        if is_TypeAlias(node):
            self.all_typehelpers.append(node)


class AddTypeHelpers(ContextAwareTransformer):
    """
    Visitor loosly based on AddImportsVisitor
    """

    CONTEXT_KEY = "AddTypeHelpers"

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        self.new_typehelpers: TypeHelpers = context.scratch.get(self.CONTEXT_KEY, [])
        self.all_typehelpers: TypeHelpers = []

    @classmethod
    def add_typevar(cls, context: CodemodContext, node: libcst.Assign):
        new_typehelpers = context.scratch.get(cls.CONTEXT_KEY, [])
        new_typehelpers.append(node)
        context.scratch[cls.CONTEXT_KEY] = new_typehelpers
        # add the typevar to the module

    def leave_Module(
        self,
        original_node: libcst.Module,
        updated_node: libcst.Module,
    ) -> libcst.Module:
        if not self.new_typehelpers:
            return updated_node

        # split the module into 3 parts
        # before and after the insertions point , and a list of the TV and TA statements
        (
            statements_before,
            helper_statements,
            statements_after,
        ) = self._split_module(original_node, updated_node)

        # simpler to compare as text than to compare the nodes -
        existing_targets = [
            helper.body[0].targets[0].target.value  # type: ignore
            for helper in helper_statements
            if is_TypeVar(helper) or is_ParamSpec(helper)
        ] + [
            helper.body[0].target.value  # type: ignore
            for helper in helper_statements
            if is_TypeAlias(helper)
        ]
        statements_to_add = []
        for new_typehelper in self.new_typehelpers:
            if isinstance(new_typehelper, libcst.AnnAssign):
                if new_typehelper.target.value not in existing_targets:  # type: ignore
                    statements_to_add.append(SimpleStatementLine(body=[new_typehelper]))
            elif isinstance(new_typehelper, libcst.Assign):
                if new_typehelper.targets[0].target.value not in existing_targets:  # type: ignore
                    statements_to_add.append(SimpleStatementLine(body=[new_typehelper]))

        body = (
            *statements_before,
            *statements_to_add,
            *statements_after,
        )

        return updated_node.with_changes(body=body)

    def _split_module(
        self,
        orig_module: libcst.Module,
        updated_module: libcst.Module,
    ) -> Tuple[Sequence[Statement], Sequence[libcst.SimpleStatementLine], Sequence[Statement]]:
        """
        Split the module into 3 parts:
        - before any TypeAlias, TypeVar or ParamSpec statements
        - the TypeAlias and TypeVar statements
        - the rest of the module after the TypeAlias and TypeVar statements
        """
        last_import = first_typehelper = last_typehelper = -1
        start = 0
        if _skip_first(orig_module):
            start = 1

        for i, statement in enumerate(orig_module.body[start:]):
            if is_import(statement):
                last_import = i + start
                continue
            if is_TypeVar(statement) or is_TypeAlias(statement) or is_ParamSpec(statement):
                if first_typehelper == -1:
                    first_typehelper = i + start
                last_typehelper = i + start
        # insert as high as possible, but after the last import and last TypeVar/TypeAlias statement
        insert_after = max(start, last_import + 1, last_typehelper + 1)
        assert insert_after != -1, "insert_after must be != -1"
        #
        before = list(updated_module.body[:insert_after])
        after = list(updated_module.body[insert_after:])
        helper_statements: Sequence[libcst.SimpleStatementLine] = list(updated_module.body[first_typehelper : last_typehelper + 1])  # type: ignore
        return (before, helper_statements, after)
