"""
Gather all TypeVar and TypeAlias assignments in a module.
"""

from typing import List, Tuple, Union

import libcst
import libcst.matchers as m
from libcst import SimpleStatementLine
from libcst.codemod._context import CodemodContext
from libcst.codemod._visitor import ContextAwareTransformer, ContextAwareVisitor
from libcst.codemod.visitors._add_imports import _skip_first
from mpflash.logger import log

_mod = libcst.parse_module("")  # Debugging aid : _mod.code_for_node(node)
_code = _mod.code_for_node  # Debugging aid : _code(node)


class GatherTypeVarsVisitor(ContextAwareVisitor):
    """
    A class for tracking visited TypeVars and TypeAliases.
    """

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        # Track all of the TypeVar assignments found in this transform
        self.all_typealias_or_vars: List[Union[libcst.Assign, libcst.AnnAssign]] = []

    def visit_Assign(self, node: libcst.Assign) -> None:
        """
        Find all TypeVar assignments in the module.
        format: T = TypeVar("T", int, float, str, bytes, Tuple)
        """
        # is this a TypeVar assignment?
        # needs to be more robust
        if isinstance(node.value, libcst.Call) and node.value.func.value == "TypeVar":  # type: ignore
            self.all_typealias_or_vars.append(node)

    def visit_AnnAssign(self, node: libcst.AnnAssign) -> None:
        """ "
        Find all TypeAlias assignments in the module.
        format: T: TypeAlias = str
        """
        if (
            isinstance(node.annotation.annotation, libcst.Name)
            and node.annotation.annotation.value == "TypeAlias"
        ):
            self.all_typealias_or_vars.append(node)


def is_TypeAlias(statement) -> bool:
    "Just the body of a simple statement" ""
    return m.matches(
        statement,
        m.AnnAssign(annotation=m.Annotation(annotation=m.Name(value="TypeAlias"))),
    )


def is_TypeVar(statement):
    "Just the body of a simple statement" ""
    r = m.matches(
        statement,
        m.Assign(value=m.Call(func=m.Name(value="TypeVar"))),
    )
    # m.SimpleStatementLine(body=[m.Assign(value=m.Call(func=m.Name(value="TypeVar")))]),
    return r


class AddTypeVarsVisitor(ContextAwareTransformer):
    """
    Visitor loosly based on AddImportsVisitor
    """

    CONTEXT_KEY = "AddTypeVarsVisitor"

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        self.new_typealias_or_vars: List[Union[libcst.Assign, libcst.AnnAssign]] = (
            context.scratch.get(self.CONTEXT_KEY, [])
        )

        self.all_typealias_or_vars: List[Union[libcst.Assign, libcst.AnnAssign]] = []

    @classmethod
    def add_typevar(cls, context: CodemodContext, node: libcst.Assign):
        new_typealias_or_vars = context.scratch.get(cls.CONTEXT_KEY, [])
        new_typealias_or_vars.append(node)
        context.scratch[cls.CONTEXT_KEY] = new_typealias_or_vars
        # add the typevar to the module

    def leave_Module(
        self,
        original_node: libcst.Module,
        updated_node: libcst.Module,
    ) -> libcst.Module:

        if not self.new_typealias_or_vars:
            return updated_node

        # split the module into 3 parts
        # before and after the insertions point , and a list of the TV and TA statements
        (
            statements_before,
            statements_after,
            tv_ta_statements,
        ) = self._split_module(original_node, updated_node)

        # TODO: avoid duplication of TypeVars and TypeAliases
        statements_to_add = []
        for new_tvta in self.new_typealias_or_vars:
            existing = False
            for existing_line in tv_ta_statements:
                try:
                    existing_tv = existing_line.body[0]  # type: ignore
                except (TypeError, IndexError):
                    # catch 'SimpleStatementLine' object is not subscriptable when the statement is not a simple statement
                    log.error("TypeVar or TypeAlias statement is not a simple statement")
                    continue

                # same type and same target?
                if (
                    is_TypeAlias(new_tvta)
                    and is_TypeAlias(existing_tv)
                    and new_tvta.target.value == existing_tv.target.value  # type: ignore
                ):
                    existing = True
                    break

                # same type and same targets?
                if (
                    is_TypeVar(new_tvta)
                    and is_TypeVar(existing_tv)
                    and new_tvta.targets[0].children[0].value == existing_tv.targets[0].children[0].value  # type: ignore
                ):
                    existing = True
                    break

            if not existing:
                statements_to_add.append(SimpleStatementLine(body=[new_tvta]))

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
    ) -> Tuple[
        List[Union[libcst.SimpleStatementLine, libcst.BaseCompoundStatement]],
        List[Union[libcst.SimpleStatementLine, libcst.BaseCompoundStatement]],
        List[Union[libcst.SimpleStatementLine, libcst.BaseCompoundStatement]],
    ]:
        """
        Split the module into 3 parts:
        - before any TypeAlias or TypeVar statements
        - the TypeAlias and TypeVar statements
        - the rest of the module after the TypeAlias and TypeVar statements
        """
        last_import = first_tv_ta = last_tv_ta = -1
        start = 0
        if _skip_first(orig_module):
            start = 1

        for i, statement in enumerate(orig_module.body[start:]):
            # todo: optimize to avoid multiple parses
            is_imp = m.matches(
                statement, m.SimpleStatementLine(body=[m.ImportFrom() | m.Import()])
            )
            if is_imp:
                last_import = i + start
            is_ta = m.matches(
                statement,
                m.SimpleStatementLine(
                    body=[
                        m.AnnAssign(annotation=m.Annotation(annotation=m.Name(value="TypeAlias")))
                    ]
                ),
            )
            is_tv = m.matches(
                statement,
                m.SimpleStatementLine(body=[m.Assign(value=m.Call(func=m.Name(value="TypeVar")))]),
            )
            if is_tv or is_ta:
                if first_tv_ta == -1:
                    first_tv_ta = i + start
                last_tv_ta = i + start
        # insert as high as possible, but after the last import and last TypeVar/TypeAlias statement
        insert_after = max(start, last_import + 1, last_tv_ta + 1)
        assert insert_after != -1, "insert_after must be != -1"
        #
        first = list(updated_module.body[:insert_after])
        last = list(updated_module.body[insert_after:])
        ta_statements = list(updated_module.body[first_tv_ta : last_tv_ta + 1])

        return (first, last, ta_statements)
