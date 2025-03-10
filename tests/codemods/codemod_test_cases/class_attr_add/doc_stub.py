# fmt: off
"""
add attribute
"""
from typing import Final


class Foo:
    ATTRIBUTE = True  # available 
    """the important docstring"""

    TYPED:bool = ...  # available 
    """the important docstring"""

    ignored  = 42  # available 
    """the important docstring"""

    FINAL = Final(42)  # available
    """the important docstring"""

    IS_OK = const(32)  # available

    EXISTING = "Should not overwrite existing"

    def foo(): ...
