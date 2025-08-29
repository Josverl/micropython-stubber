"""Test for base class discovery functionality in createstubs.py"""

import pytest
from typing import Any, Generator

from shared import LOCATIONS, VARIANTS, import_variant

pytestmark = [pytest.mark.stubber, pytest.mark.micropython]


class TestBaseClasses:
    """Test classes for base class discovery."""
    
    class SimpleBase:
        pass
    
    class DerivedClass(SimpleBase):
        pass
    
    class CustomException(Exception):
        pass
    
    class CustomError(ValueError):
        pass
    
    class MultipleInheritance(SimpleBase, dict):
        pass


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_discover_base_classes_function(
    location: Any,
    variant: str,
    mock_micropython_path: Generator[str, None, None],
):
    """Test the _discover_base_classes function directly."""
    createstubs = import_variant(location, variant)
    
    # Test simple inheritance
    result = createstubs._discover_base_classes(TestBaseClasses.DerivedClass, "DerivedClass")
    assert result == "SimpleBase", f"Expected 'SimpleBase', got '{result}'"
    
    # Test exception inheritance using __bases__
    result = createstubs._discover_base_classes(TestBaseClasses.CustomException, "CustomException")
    assert result == "Exception", f"Expected 'Exception', got '{result}'"
    
    # Test value error inheritance
    result = createstubs._discover_base_classes(TestBaseClasses.CustomError, "CustomError")
    assert result == "ValueError", f"Expected 'ValueError', got '{result}'"
    
    # Test multiple inheritance
    result = createstubs._discover_base_classes(TestBaseClasses.MultipleInheritance, "MultipleInheritance")
    assert result == "SimpleBase, dict", f"Expected 'SimpleBase, dict', got '{result}'"
    
    # Test class with only object as base (should return empty string)
    result = createstubs._discover_base_classes(TestBaseClasses.SimpleBase, "SimpleBase")
    assert result == "", f"Expected empty string, got '{result}'"


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_discover_base_classes_fallback(
    location: Any,
    variant: str,
    mock_micropython_path: Generator[str, None, None],
):
    """Test fallback behavior when __bases__ is not available."""
    createstubs = import_variant(location, variant)
    
    # Test exception fallback (when class_instance is None)
    result = createstubs._discover_base_classes(None, "SomeException")
    assert result == "Exception", f"Expected 'Exception', got '{result}'"
    
    # Test error fallback
    result = createstubs._discover_base_classes(None, "SomeError")
    assert result == "Exception", f"Expected 'Exception', got '{result}'"
    
    # Test special exception classes
    result = createstubs._discover_base_classes(None, "KeyboardInterrupt")
    assert result == "Exception", f"Expected 'Exception', got '{result}'"
    
    # Test BaseException special case (should not inherit from Exception)
    result = createstubs._discover_base_classes(None, "BaseException")
    assert result == "", f"Expected empty string, got '{result}'"
    
    # Test regular class fallback
    result = createstubs._discover_base_classes(None, "RegularClass")
    assert result == "", f"Expected empty string, got '{result}'"


@pytest.mark.parametrize("variant", VARIANTS)  
@pytest.mark.parametrize("location", LOCATIONS)
def test_discover_base_classes_builtin(
    location: Any,
    variant: str,
    mock_micropython_path: Generator[str, None, None],
):
    """Test with built-in Python classes."""
    createstubs = import_variant(location, variant)
    
    # Test built-in exception
    result = createstubs._discover_base_classes(ValueError, "ValueError")
    assert result in ["Exception", ""], f"Unexpected result for ValueError: '{result}'"
    
    # Test BaseException
    result = createstubs._discover_base_classes(BaseException, "BaseException")
    # BaseException should have no base classes or empty string in our implementation
    assert result in ["", "object"], f"Unexpected result for BaseException: '{result}'"
    
    # Test basic types (should have no meaningful base classes for our purposes)
    result = createstubs._discover_base_classes(dict, "dict")
    assert result == "", f"Expected empty string for dict, got '{result}'"
    
    result = createstubs._discover_base_classes(list, "list")
    assert result == "", f"Expected empty string for list, got '{result}'"