"""
simple functions and classes
"""


def foo(pin: int, /, limit: int = 100) -> str:
    "function foo"
    pass


class Bar:
    "Class Docstring"
    def foo(y: int, x: int = 10) -> int:
        "Method foo Docstring"
        return 1
