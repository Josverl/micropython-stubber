# fmt: off
"""
add typealias that already is defined
"""
from typing_extensions import TypeAlias

UUID: TypeAlias = str
_Flag: TypeAlias = int
_Descriptor: TypeAlias = tuple["UUID", _Flag]

def const(): ...


def bar(): ...
