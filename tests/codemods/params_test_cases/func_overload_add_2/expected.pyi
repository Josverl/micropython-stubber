# fmt: off
"""
Overloaded functions, retain existing docstrings
"""
from typing import Literal, overload

@overload
def foo(value: int) -> None:
    """
    Existing Docstring
    with multiple lines
    """
    ...

@overload
def foo(value: None) -> str:
    """
    Existing Docstring
    with multiple lines
    """
    ...

@overload
def bar(value: Literal["s"]) -> str: ...
@overload
def bar(value: Literal["d"]) -> int: ...

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
