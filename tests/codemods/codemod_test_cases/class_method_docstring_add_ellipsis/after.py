"""
simple functions and classes
"""
# fmt: off

def foo(pin: int, /, limit: int = 100) -> str:
    "function foo"
    ...


class Bar:
    "Class Docstring"
    def foo(self, y: int, x: int = 10) -> int:
        "Method foo Docstring"
        ...
