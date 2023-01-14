from __future__ import annotations
from libcst import matchers as m
from libcst.matchers._visitors import _gather_constructed_leave_funcs, _gather_constructed_visit_funcs
from typing import Optional
import itertools


class ScopeableMatcherTransformer(m.MatcherDecoratableTransformer):
    """MatcherDecoratableTransformer that can be reused with different scopes."""

    scope_matcher: Optional[m.BaseMatcherNode]

    def __init__(self):
        super().__init__()

    def _build_scoped_meth(self, method_name: str, scope_matcher: m.BaseMatcherNode):
        """Build unbound scoped method from parent class."""
        unbound_meth = getattr(type(self), method_name)
        unbound_meth.__dict__.pop("_call_if_inside_matcher", None)
        return m.call_if_inside(scope_matcher)(unbound_meth)

    def with_scope(self, scope_matcher: m.BaseMatcherNode) -> m.MatcherDecoratableTransformer:
        """Construct a copy of this matcher with visitors scoped to `scope_matcher.`"""
        constructed_meths = list(
            itertools.chain.from_iterable(
                [*_gather_constructed_leave_funcs(self).values(), *_gather_constructed_visit_funcs(self).values()]
            )
        )
        scoped_meths = {f.__name__: self._build_scoped_meth(f.__name__, scope_matcher) for f in constructed_meths}
        inst_vars = {k: v for k, v in vars(self).items() if k not in {"_matchers", "_extra_leave_funcs", "_extra_visit_funcs"}}
        # create a dynamically derived class with the transform meth wrapped with scope check.
        klass = type(
            f"{self.__class__.__name__}_{repr(scope_matcher)}",
            (m.MatcherDecoratableTransformer,),
            {**inst_vars, **scoped_meths, "scope_matcher": scope_matcher},
        )
        return klass()
