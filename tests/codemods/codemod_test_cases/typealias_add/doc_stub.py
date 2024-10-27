# fmt: off
"""
add typealias
"""


from typing import TypeAlias

UUID: TypeAlias = str
_Flag: TypeAlias = int
_Descriptor: TypeAlias = tuple["UUID", _Flag]
_Characteristic: TypeAlias = (tuple["UUID", _Flag] | tuple["UUID", _Flag, tuple[_Descriptor, ...]])
_Service: TypeAlias = tuple["UUID", tuple[_Characteristic, ...]]
x = 2

def bar(f:_Flag , d:_Descriptor   ) -> _Service:
    """
    Used to declare that the expression is a constant so that the compiler can
    optimise it.  The use of this function should be as follows::
    """
    ...
