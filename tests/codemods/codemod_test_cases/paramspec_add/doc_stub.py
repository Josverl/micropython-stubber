# fmt: off
"""
add ParamSpec
"""

from typing import Callable, TypeVar, ParamSpec
import functools

_Ret = TypeVar("_Ret")
_Param = ParamSpec("_Param")

def native(_func: Callable[_Param, _Ret], /) -> Callable[_Param, _Ret]:
    ...

