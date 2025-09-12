# fmt: off
"""
Test overwrite existing literal docstrings - doc version
"""

# Constant with new docstring (but existing should be preserved)
EXISTING_CONST = 42
"""New docstring - should overwrite"""

# Constant without docstring - should get this one
NEW_CONST = 100
"""New constant documentation"""

# Another one with different docstring
ANOTHER_EXISTING = "value"
"""Different docstring - should overwrite"""

class TestClass:
    """Test class with documentation"""
    
    # Class constant with new docstring (existing should be preserved)
    CLASS_EXISTING = 1
    """New class docstring - should overwrite"""
    
    # Class constant without docstring - should get this one
    CLASS_NEW = 2
    """New class constant documentation"""
    
    def method(self):
        """Method with documentation"""
        ...
