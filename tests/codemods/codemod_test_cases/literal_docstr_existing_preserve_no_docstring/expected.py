# fmt: off
"""
Test preserving existing literal docstrings
"""

# Constant with existing docstring - should not be overwritten
EXISTING_CONST = 42
"""OK Original docstring - keep this"""

# Constant without docstring - should get one from doc_stub
NEW_CONST = 100
"""OK New constant documentation"""

# Another existing one
ANOTHER_EXISTING = "value"
"""OK Another original docstring - keep this"""

class TestClass:

    # Class constant with existing docstring
    CLASS_EXISTING = 1
    """OK Existing class docstring - keep this"""

    # Class constant without docstring
    CLASS_NEW = 2
    """OK New class constant documentation"""

    def method(self):
        """OK Method with documentation"""
        ...
