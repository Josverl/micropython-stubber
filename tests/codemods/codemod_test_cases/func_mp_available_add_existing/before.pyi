#fmt: off
"""
mp_available functions
"""

from typing import overload
from _mpy_shed import mp_available

@mp_available
def foo(value: int) -> None:
    """
    Set foo value
    First overload
    """
    ...


@mp_available
def foo(value: None) -> str:
    """
    Get foo value
    Second overload
    """
    ...
