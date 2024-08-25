# fmt: off
"""
Overloaded functions
"""
from typing import overload


@overload
def foo(value: bytes) -> str:
    """
    Bytes to str
    Existing overload A
    """
    ...

@overload
def foo(value: list) -> str:
    """
    list to str
    Existing overload B
    """
    ...


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
