# fmt: off
"""
Test overwrite existing literal docstrings
"""

# Constant with existing docstring - should not be overwritten
EXISTING_CONST = 42
"""Original docstring - keep this"""

# Constant without docstring - should get one from doc_stub
NEW_CONST = 100

# Another existing one
ANOTHER_EXISTING = "value"
"""Another original docstring"""

class TestClass:
    """Test class"""
    
    # Class constant with existing docstring
    CLASS_EXISTING = 1
    """Existing class docstring"""
    
    # Class constant without docstring
    CLASS_NEW = 2
    
    def method(self): ...
