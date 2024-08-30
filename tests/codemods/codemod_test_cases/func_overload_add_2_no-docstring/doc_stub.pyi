"""
Overloaded functions
"""

from typing import Literal, overload

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

@overload
def baz(value: int) -> None:
    """
    Set baz value
    First overload
    """
    ...

@overload
def baz(value: None) -> str:
    """
    Get baz value
    Second overload
    """
    ...

@overload
def bar(value: Literal["s"]) -> str: ...
@overload
def bar(value: Literal["d"]) -> int: ...
