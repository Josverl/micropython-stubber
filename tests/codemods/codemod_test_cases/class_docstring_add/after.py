"""
simple functions and classes
"""


def foo(pin: int, /, limit: int = 100) -> str:
    "function foo"
    ...


def dorf():
    """"""
    ...


class Bar:
    "Class Docstring"
    def foo(self, y: int, x: int = 10) -> int:
        "Method foo Docstring"
        return 1


class Bork:
    """"""

    def blurf(self):
        """"""
        return 1
