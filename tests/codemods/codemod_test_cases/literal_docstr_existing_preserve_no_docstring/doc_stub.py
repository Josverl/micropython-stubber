# fmt: off
"""
Test preserving existing literal docstrings - doc version
"""

# Constant with new docstring (but existing should be preserved)
EXISTING_CONST = 42
"""FAIL New docstring - should not overwrite"""

# Constant without docstring - should get this one
NEW_CONST = 100
"""OK New constant documentation"""

# Another one with different docstring
ANOTHER_EXISTING = "value"
"""FAIL Different docstring - should not overwrite"""

class TestClass:
    
    # Class constant with new docstring (existing should be preserved)
    CLASS_EXISTING = 1
    """FAIL New class docstring - should not overwrite"""
    
    # Class constant without docstring - should get this one
    CLASS_NEW = 2
    """OK New class constant documentation"""
    
    def method(self):
        """OK Method with documentation"""
        ...
