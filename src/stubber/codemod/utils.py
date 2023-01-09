from __future__ import annotations
from libcst import matchers as m
from libcst.matchers._visitors import _gather_constructed_leave_funcs, _gather_constructed_visit_funcs
from typing import Optional
import itertools


class ScopeableMatcherTransformer(m.MatcherDecoratableTransformer):
    """MatcherDecoratableTransformer that can be reused with different scopes."""

    scope_matcher: Optional[m.BaseMatcherNode]

    def __init__(self, *, scope_matcher: Optional[m.BaseMatcherNode] = None):
        self.scope_matcher = scope_matcher
        if self.scope_matcher is not None:
            constructed_meths = list(
                itertools.chain.from_iterable(
                    [*_gather_constructed_leave_funcs(self).values(), *_gather_constructed_visit_funcs(self).values()]
                )
            )
            scoped_meths = {
                f.__name__: m.call_if_inside(self.scope_matcher)(getattr(self.__class__, f.__name__)) for f in constructed_meths
            }
            # create a dynamically derived class with the transform meth wrapped with scope check.
            self.__class__ = type(f"{self.__class__.__name__}_{repr(self.scope_matcher)}", (self.__class__,), scoped_meths)
        super().__init__()
