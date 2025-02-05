# fmt: off
"""
Overloaded functions
"""
from typing import overload

def bar(): ...


@overload
def foo(value: int) -> None:
    """
    Set foo value
    First overload
    """
    ...


@overload
def foo(value: None) -> str:
    """
    Get foo value
    Second overload
    """
    ...
