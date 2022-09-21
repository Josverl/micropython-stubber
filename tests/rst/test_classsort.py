# others
import pytest

# pytest.skip("---===*** DEBUGGING ***===---", allow_module_level=True)
# mark all tests 
pytestmark = pytest.mark.doc_stubs

# SOT
from stubber.rst import sort_classes


def test_sort_classes():
    classes = ["class Spam(Foo)", "class Foo(Bar)", "class Bar(Parrot)", "class Parrot()"]

    sorted = sort_classes(classes)
    assert sorted != None
    assert len(sorted) == len(classes)
    assert sorted[0] == "class Parrot()"
    assert sorted[1] == "class Bar(Parrot)"
    assert sorted[2] == "class Foo(Bar)"
    assert sorted[3] == "class Spam(Foo)"


def test_sort_classes_1():
    classes = ["class Spam(Foo)"]
    sorted = sort_classes(classes)
    assert sorted != None
    assert len(sorted) == len(classes)
    assert sorted[0] == "class Spam(Foo)"


def test_sort_classes_empty():
    classes = []
    sorted = sort_classes(classes)
    assert sorted != None
    assert len(sorted) == len(classes)
    assert sorted == []


def test_sort_classes_basic():
    # short notation without ()
    classes = ["class Foo", "class Bar"]
    sorted = sort_classes(classes)
    assert sorted != None
    assert len(sorted) == len(classes)
    # no sort order defined ...


def test_sort_classes_full():
    # full
    classes = ["class Foo(Bar):", "class Bar():"]
    sorted = sort_classes(classes)
    assert sorted != None
    assert len(sorted) == len(classes)
    assert sorted[0] == "class Bar():"
    assert sorted[1] == "class Foo(Bar):"
