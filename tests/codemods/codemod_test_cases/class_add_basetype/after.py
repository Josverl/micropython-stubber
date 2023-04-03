"""
add base type to class definition
"""
# fmt: off

class Bar(enum):
    "Class Docstring"
    def foo(self, y: int, x: int = 10) -> int:
        "Method foo Docstring"
        return 1
