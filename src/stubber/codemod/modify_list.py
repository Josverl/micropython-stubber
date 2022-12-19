from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence, Optional

import libcst as cst
from libcst import matchers as m


@dataclass(kw_only=True)
class ListChangeSet:
    add: Sequence[cst.BaseExpression] = field(default_factory=list)
    remove: Sequence[m.BaseMatcherNode] = field(default_factory=list)
    replace: bool = False

    @classmethod
    def from_strings(
        cls, *, add: Optional[Sequence[str]] = None, remove: Optional[Sequence[str]] = None, replace: bool = False
    ) -> ListChangeSet:
        add_nodes = [cst.SimpleString(f'"{s}"') for s in add] if add else []
        remove_nodes = [m.SimpleString(f'"{s}"') for s in remove or list()] if remove else []
        return ListChangeSet(add=add_nodes, remove=remove_nodes, replace=replace)


class ModifyListElements(m.MatcherDecoratableTransformer):
    scope_matcher: Optional[m.BaseMatcherNode]
    change_set: ListChangeSet

    def __init__(self, *, change_set: ListChangeSet, scope_matcher: Optional[m.BaseMatcherNode] = None):
        self.scope_matcher = scope_matcher
        self.change_set = change_set
        if self.scope_matcher:
            # create a dynamically derived class with the transform meth wrapped with scope check.
            self.__class__ = type(
                f"{self.__class__.__name__}_{repr(scope_matcher)}",
                (self.__class__,),
                {"modify_list_elements": m.call_if_inside(scope_matcher)(self.__class__.modify_list_elements)},
            )
        super().__init__()

    @m.leave(m.List())
    def modify_list_elements(self, original_node: cst.List, updated_node: cst.List) -> cst.List:
        current_elements = [e.value for e in original_node.elements if not any(self.matches(e.value, r) for r in self.change_set.remove)]
        new_elements = [] if self.change_set.replace else current_elements
        new_elements.extend(self.change_set.add)

        new_list = cst.List(elements=[cst.Element(value=cst.helpers.ensure_type(e, cst.BaseExpression)) for e in new_elements])

        return updated_node.with_changes(elements=new_list.elements)
