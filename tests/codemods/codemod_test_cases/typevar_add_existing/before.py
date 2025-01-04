# fmt: off
"""
add typevar
"""
from typing import Tuple, TypeVar

# Foo = TypeVar("Foo",  Tuple)  
Const_T = TypeVar("Const_T", int, float, str, bytes, Tuple)

def const(): ...


def bar(): ...
