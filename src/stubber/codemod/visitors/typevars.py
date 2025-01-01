"""
Gather all TypeVar assignments in a module.
"""

from typing import List, Tuple, Union

import libcst
from libcst import SimpleStatementLine, matchers, parse_statement
from libcst.codemod._context import CodemodContext
from libcst.codemod._visitor import ContextAwareTransformer, ContextAwareVisitor
from libcst.codemod.visitors._add_imports import _skip_first

_empty_module = libcst.parse_module("")  # Debugging aid : empty_module.code_for_node(node)


class GatherTypeVarsVisitor(ContextAwareVisitor):
    """
    A class for tracking visited TypeVars.
    """

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        # Track all of the TypeVar assignments found in this transform
        self.all_typevars: List[Union[libcst.Assign, libcst.AnnAssign]] = []

    def visit_Assign(self, node: libcst.Assign) -> None:
        """
        Find all TypeVar assignments in the module.
        format: T = TypeVar("T", int, float, str, bytes, Tuple)
        """
        # is this a TypeVar assignment?
        # needs to be more robust
        if isinstance(node.value, libcst.Call) and node.value.func.value == "TypeVar":
            self.all_typevars.append(node)

    def visit_AnnAssign(self, node: libcst.AnnAssign) -> None:
        """ "
        Find all TypeAlias assignments in the module.
        format: T: TypeAlias = str
        """
        if isinstance(node.annotation.annotation, libcst.Name) and node.annotation.annotation.value == "TypeAlias":
            self.all_typevars.append(node)


class AddTypeVarsVisitor(ContextAwareTransformer):
    # loosly based on AddImportsVisitor
    CONTEXT_KEY = "AddTypeVarsVisitor"

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        self.typevars: List[libcst.Assign] = context.scratch.get(self.CONTEXT_KEY, [])

        self.all_typevars: List[libcst.Assign] = []

    @classmethod
    def add_typevar(cls, context: CodemodContext, node: libcst.Assign):
        typevars = context.scratch.get(cls.CONTEXT_KEY, [])
        typevars.append(node)
        context.scratch[cls.CONTEXT_KEY] = typevars
        # add the typevar to the module

    def visit_Module(self, node: libcst.Module) -> None:
        self.all_typevars = []
        ...

    def leave_Module(
        self,
        original_node: libcst.Module,
        updated_node: libcst.Module,
    ) -> libcst.Module:

        if not self.typevars:
            return updated_node

        # split the module into 3 parts
        # before the first import, the imports, and after the imports
        (
            statements_before_imports,
            statements_until_add_imports,
            statements_after_imports,
        ) = self._split_module(original_node, updated_node)

        typevar_statements = [SimpleStatementLine(body=[tv]) for tv in self.typevars]
        body = (
            *statements_before_imports,
            *statements_until_add_imports,
            *typevar_statements,
            *statements_after_imports,
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
        # method copied from AddImportsVisitor
        # can likely be simplified for typevars
        statement_before_import_location = 0
        import_add_location = 0

        # This works under the principle that while we might modify node contents,
        # we have yet to modify the number of statements. So we can match on the
        # original tree but break up the statements of the modified tree. If we
        # change this assumption in this visitor, we will have to change this code.

        # Finds the location to add imports. It is the end of the first import block that occurs before any other statement (save for docstrings)

        # Never insert an import before initial __strict__ flag or docstring
        if _skip_first(orig_module):
            statement_before_import_location = import_add_location = 1

        for i, statement in enumerate(orig_module.body[statement_before_import_location:]):
            if matchers.matches(
                statement,
                matchers.SimpleStatementLine(body=[matchers.ImportFrom() | matchers.Import()]),
            ):
                import_add_location = i + statement_before_import_location + 1
            else:
                break

        return (
            list(updated_module.body[:statement_before_import_location]),
            list(updated_module.body[statement_before_import_location:import_add_location]),
            list(updated_module.body[import_add_location:]),
        )
