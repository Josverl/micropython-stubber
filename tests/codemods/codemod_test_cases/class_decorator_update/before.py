"""
add decorator to class definition
"""
# fmt: off
@before_decorator
class Bar:
    def foo(self):
        return 1
