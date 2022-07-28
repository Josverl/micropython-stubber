# docstrings


def foo(pin: int, /, limit: int = 100) -> str:
    "function foo"
    ...


class Bar:
    "Class Docstring"
    def foo(y: int, x: int = 10) -> int:
        "Method foo Docstring"
        return 1
