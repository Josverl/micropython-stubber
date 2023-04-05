# docstrings

@dataclass
class Bar:
    "Class Docstring"

    def foo(self, y: int, x: int = 10) -> int:
        "Method foo Docstring"
        return 1
