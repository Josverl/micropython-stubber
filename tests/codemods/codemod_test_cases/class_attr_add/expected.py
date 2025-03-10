# fmt: off
"""
add attribute
"""
from typing import Final


class Foo:
    EXISTING = "Do not overwrite me"
    ATTRIBUTE = True
    TYPED:bool = ...
    FINAL = Final(42)
    IS_OK = const(32)

    def foo(): ...


    def bar(): ...
