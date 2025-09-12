# fmt: off
"""
Test overwrite existing literal docstrings - doc version

---
Test overwrite existing literal docstrings
"""

# Constant with existing docstring - should not be overwritten
EXISTING_CONST = 42
"""New docstring - should overwrite"""

# Constant without docstring - should get one from doc_stub
NEW_CONST = 100
"""New constant documentation"""

# Another existing one
ANOTHER_EXISTING = "value"
"""Different docstring - should overwrite"""

class TestClass:
    """Test class with documentation"""

    # Class constant with existing docstring
    CLASS_EXISTING = 1
    """New class docstring - should overwrite"""

    # Class constant without docstring
    CLASS_NEW = 2
    """New class constant documentation"""

    def method(self):
        """Method with documentation"""
        ...
