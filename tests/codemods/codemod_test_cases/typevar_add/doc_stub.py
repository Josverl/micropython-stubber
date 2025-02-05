# fmt: off
"""
add typevar
"""


from typing import Tuple, TypeVar

Const_T = TypeVar("Const_T", int, float, str, bytes, Tuple)  # constant

x = 2 

def const(expr: Const_T, /) -> Const_T:
    """
    Used to declare that the expression is a constant so that the compiler can
    optimise it.  The use of this function should be as follows::
    """
    ...
