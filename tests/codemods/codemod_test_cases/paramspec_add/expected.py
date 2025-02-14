#fmt: off
"""
add ParamSpec
"""
import functools
from typing import Callable, ParamSpec, TypeVar

_Ret = TypeVar("_Ret")
_Param = ParamSpec("_Param")


def native(_func: Callable[_Param, _Ret], /) -> Callable[_Param, _Ret]: ...


def foo(): ...
