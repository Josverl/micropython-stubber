#fmt: off
"""
add ParamSpec
"""

from typing import Callable, TypeVar, ParamSpec
import functools

_Param = ParamSpec("_Param")
_Ret = TypeVar("_Ret")

def native(_func: Callable[_Param, _Ret], /) -> Callable[_Param, _Ret]: ...


def foo(): ...
