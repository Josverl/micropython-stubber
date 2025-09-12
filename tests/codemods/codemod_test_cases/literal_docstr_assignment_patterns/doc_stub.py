# fmt: off
"""
Test various assignment patterns for literal docstrings - doc version
"""
from typing import Final

# Regular assignment
SIMPLE_CONST = 42
"""Simple integer constant"""

# Annotated assignment
TYPED_CONST: int = 100
"""Typed integer constant"""

# Final annotation
FINAL_CONST: Final = 200
"""Final constant value"""

# String constant
STRING_CONST = "hello"
"""String constant value"""

# Boolean constant
BOOL_CONST = True
"""Boolean constant value"""

# Multiple targets (not supported - should be ignored)
A = B = 300

class TestClass:
    """Test class for assignment patterns with documentation"""
    
    # Class-level regular assignment
    CLASS_SIMPLE = 1
    """Simple class constant"""
    
    # Class-level annotated assignment
    CLASS_TYPED: str = "test"
    """Typed class constant"""
    
    # Class-level Final
    CLASS_FINAL: Final = 99
    """Final class constant"""
    
    def method(self):
        """Test method"""
        ...