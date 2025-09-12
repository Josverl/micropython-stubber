# fmt: off
"""
Test various assignment patterns for literal docstrings
"""
from typing import Final

# Regular assignment
SIMPLE_CONST = 42

# Annotated assignment
TYPED_CONST: int = 100

# Final annotation
FINAL_CONST: Final = 200

# String constant
STRING_CONST = "hello"

# Boolean constant  
BOOL_CONST = True

# Multiple targets (not supported - should be ignored)
A = B = 300

class TestClass:
    """Test class for assignment patterns"""
    
    # Class-level regular assignment
    CLASS_SIMPLE = 1
    
    # Class-level annotated assignment
    CLASS_TYPED: str = "test"
    
    # Class-level Final
    CLASS_FINAL: Final = 99
    
    def method(self): ...