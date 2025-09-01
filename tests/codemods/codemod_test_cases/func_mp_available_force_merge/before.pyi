"""
Target before
"""

from typing import Callable, ParamSpec, TypeVar

from _mpy_shed import mp_available

_Param = ParamSpec("_Param")
_Ret = TypeVar("_Ret")

@mp_available()  # force merge
def native(_func: Callable[_Param, _Ret], /) -> Callable[_Param, _Ret]:
    """
    This causes the MicroPython compiler to emit native CPU opcodes rather than bytecode.
    It covers the bulk of the MicroPython functionality, so most functions will require no adaptation.
    See: https://docs.micropython.org/en/latest/reference/speed_python.html#the-native-code-emitter
    """
    ...
