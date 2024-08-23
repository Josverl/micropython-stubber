# fmt: off
"""
Overloaded functions
"""
from typing import overload

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
def foo(value: str) -> None:
    """
    Get foo string
    Third overload
    """
    ...


def process(): ...
