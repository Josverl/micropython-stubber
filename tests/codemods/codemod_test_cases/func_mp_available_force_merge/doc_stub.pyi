"""
Docstub for native function
"""

from typing import Callable, ParamSpec, TypeVar

from _mpy_shed import mp_available

_Param = ParamSpec("_Param")
_Ret = TypeVar("_Ret")

@mp_available(["esp32", "rp2"])  # args shouldn't matter for detection
def native(_func: Callable[_Param, _Ret], /) -> Callable[_Param, _Ret]:
    """Docstub docstring from docs"""
    ...
