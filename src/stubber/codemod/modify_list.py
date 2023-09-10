from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence, Optional

import libcst as cst
from libcst import matchers as m
from stubber.codemod.utils import ScopeableMatcherTransformer


@dataclass
class ListChangeSet:
    """Describes a set of changes to be made to a list.
    - add: a list of elements to add to the list
    - remove: a list of elements to remove from the list
    - replace: if True, the list will be replaced with the elements in add
    """

    add: Sequence[cst.BaseExpression] = field(default_factory=list)
    remove: Sequence[m.BaseMatcherNode] = field(default_factory=list)
    replace: bool = False

    @classmethod
    def from_strings(
        cls, *, add: Optional[Sequence[str]] = None, remove: Optional[Sequence[str]] = None, replace: bool = False
    ) -> ListChangeSet:
        add_nodes = [cst.SimpleString(f'"{s}"') for s in add] if add else []
        remove_nodes = (
            [m.SimpleString(f'"{s}"') for s in remove or []] if remove else []
        )
        return ListChangeSet(add=add_nodes, remove=remove_nodes, replace=replace)


class ModifyListElements(ScopeableMatcherTransformer):
    """
    Modifies the elements of a list (i.e, of modules to stub or exclude),
    adding and removing elements as specified in the change_set.
    """

    change_set: ListChangeSet

    def __init__(self, *, change_set: ListChangeSet):
        self.change_set = change_set
        super().__init__()

    @m.leave(m.List())
    def modify_list_elements(self, original_node: cst.List, updated_node: cst.List) -> cst.List:
        current_elements = [e.value for e in original_node.elements if not any(self.matches(e.value, r) for r in self.change_set.remove)]
        new_elements = [] if self.change_set.replace else current_elements
        new_elements.extend(self.change_set.add)

        new_list = cst.List(elements=[cst.Element(value=cst.ensure_type(e, cst.BaseExpression)) for e in new_elements])

        return updated_node.with_changes(elements=new_list.elements)
