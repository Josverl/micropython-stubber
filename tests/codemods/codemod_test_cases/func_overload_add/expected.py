"""
Overloaded functions
"""

# fmt: off
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
