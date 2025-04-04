# fmt: off
"""
add typealias that already is defined
"""
from typing_extensions import TypeAlias

UUID: TypeAlias = str
_Flag: TypeAlias = int
_Descriptor: TypeAlias = tuple["UUID", _Flag]
NEW_TA: TypeAlias = str
_Characteristic: TypeAlias = (tuple["UUID", _Flag] | tuple["UUID", _Flag, tuple[_Descriptor, ...]])
_Service: TypeAlias = tuple["UUID", tuple[_Characteristic, ...]]

def const(): ...


def bar(f:_Flag , d:_Descriptor   ) -> _Service:
    """
    Used to declare that the expression is a constant so that the compiler can
    optimise it.  The use of this function should be as follows::
    """
    ...
