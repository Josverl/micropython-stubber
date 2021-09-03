# others
from typing import Dict, List, Union
import pytest

# SOT
from rst.classsort import sort_classes


def test_sort_classes():
    classes = ["class Spam(Foo)", "class Foo(Bar)", "class Bar(Parrot)", "class Parrot()"]

    sorted = sort_classes(classes)
    assert sorted != None
    assert sorted[0] == "class Parrot()"
    assert sorted[1] == "class Bar(Parrot)"
    assert sorted[2] == "class Foo(Bar)"
    assert sorted[3] == "class Spam(Foo)"


def test_sort_classes_1():
    classes = [
        "class Spam(Foo)",
    ]

    sorted = sort_classes(classes)
    assert sorted != None
    assert sorted[0] == "class Spam(Foo)"


def test_sort_classes_empty():
    classes = []
    sorted = sort_classes(classes)
    assert sorted != None
    assert sorted == []

