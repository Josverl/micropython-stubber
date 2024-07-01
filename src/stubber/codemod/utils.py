from __future__ import annotations
from libcst import matchers as m
from libcst.matchers._visitors import _gather_constructed_leave_funcs, _gather_constructed_visit_funcs # type: ignore
from typing import Any, Optional
from types import FunctionType
import itertools


def shallow_copy_function(func: Any) -> FunctionType:
    """Create a shallow copy of the given function.

    The returned function is unbound and does not copy
    attributes defined on the function.

    """
    return FunctionType(
        func.__code__,
        func.__globals__,
        name=func.__name__,
        argdefs=getattr(func, "__defaults__", None),
        closure=getattr(func, "__closure__", None),
    )


class ScopeableMatcherTransformer(m.MatcherDecoratableTransformer):
    """MatcherDecoratableTransformer that can be reused with different scopes."""

    scope_matcher: Optional[m.BaseMatcherNode]

    def __init__(self):
        super().__init__()

    def _build_scoped_meth(self, method_name: str, scope_matcher: m.BaseMatcherNode):
        """Build unbound scoped method from parent class."""
        bound_meth = getattr(type(self), method_name)
        matchers = {k: v for k, v in bound_meth.__dict__.items() if k in {"_leave_matcher", "_visit_matcher"}}
        unbound_meth = shallow_copy_function(bound_meth)
        unbound_meth.__dict__.update(matchers)
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
