"""
add decorator to class definition
"""
# fmt: off
@dataclass
@before_decorator
class Bar:
    "Class Docstring"
    def foo(self, y: int, x: int = 10) -> int:
        "Method foo Docstring"
        return 1
