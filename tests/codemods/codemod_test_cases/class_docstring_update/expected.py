# fmt: off
"""
simple functions and classes
"""


def foo():
    ...


def dorf():
    """"""
    ...


class Bar:
    "OK - Class Docstring"
    def foo(self, y: int, x: int = 10) -> int:
        "OK - Method foo Docstring"
        return 1


class Bork:
    """"""

    def blurf(self):
        """"""
        return 1
