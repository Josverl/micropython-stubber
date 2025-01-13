"""
Access binary data in a structured way.

MicroPython module: https://docs.micropython.org/en/v1.24.0/library/uctypes.html

This module implements "foreign data interface" for MicroPython. The idea
behind it is similar to CPython's ``ctypes`` modules, but the actual API is
different, streamlined and optimized for small size. The basic idea of the
module is to define data structure layout with about the same power as the
C language allows, and then access it using familiar dot-syntax to reference
sub-fields.
"""

# source version: v1.24.1
# origin module:: repos/micropython/docs/library/uctypes.rst
from __future__ import annotations

from _mpy_shed import AnyReadableBuf
from _typeshed import Incomplete
from typing_extensions import TypeAlias

_ScalarProperty: TypeAlias = int
_RecursiveProperty: TypeAlias = tuple[int, _property]
_ArrayProperty: TypeAlias = tuple[int, int]
_ArrayOfAggregateProperty: TypeAlias = tuple[int, int, _property]
_PointerToAPrimitiveProperty: TypeAlias = tuple[int, int]
_PointerToAaAggregateProperty: TypeAlias = tuple[int, "_property"]
_BitfieldProperty: TypeAlias = int
_property: TypeAlias = (
    _ScalarProperty
    | _RecursiveProperty
    | _ArrayProperty
    | _ArrayOfAggregateProperty
    | _PointerToAPrimitiveProperty
    | _PointerToAaAggregateProperty
    | _BitfieldProperty
)
_descriptor: TypeAlias = tuple[str, _property]

LITTLE_ENDIAN: bytes
"""\
Layout type for a little-endian packed structure. (Packed means that every
field occupies exactly as many bytes as defined in the descriptor, i.e.
the alignment is 1).
"""
BIG_ENDIAN: Incomplete
"""Layout type for a big-endian packed structure."""
NATIVE: Incomplete
"""\
Layout type for a native structure - with data endianness and alignment
conforming to the ABI of the system on which MicroPython runs.
"""
UINT8: int
"""\
Integer types for structure descriptors. Constants for 8, 16, 32,
and 64 bit types are provided, both signed and unsigned.
"""
INT8: int
"""\
Integer types for structure descriptors. Constants for 8, 16, 32,
and 64 bit types are provided, both signed and unsigned.
"""
UINT16: int
"""\
Integer types for structure descriptors. Constants for 8, 16, 32,
and 64 bit types are provided, both signed and unsigned.
"""
INT16: int
"""\
Integer types for structure descriptors. Constants for 8, 16, 32,
and 64 bit types are provided, both signed and unsigned.
"""
UINT32: int
"""\
Integer types for structure descriptors. Constants for 8, 16, 32,
and 64 bit types are provided, both signed and unsigned.
"""
INT32: int
"""\
Integer types for structure descriptors. Constants for 8, 16, 32,
and 64 bit types are provided, both signed and unsigned.
"""
UINT64: int
"""\
Integer types for structure descriptors. Constants for 8, 16, 32,
and 64 bit types are provided, both signed and unsigned.
"""
INT64: int
"""\
Integer types for structure descriptors. Constants for 8, 16, 32,
and 64 bit types are provided, both signed and unsigned.
"""
FLOAT32: Incomplete
"""Floating-point types for structure descriptors."""
FLOAT64: Incomplete
"""Floating-point types for structure descriptors."""
VOID: Incomplete
"""\
``VOID`` is an alias for ``UINT8``, and is provided to conveniently define
C's void pointers: ``(uctypes.PTR, uctypes.VOID)``.
"""
PTR: Incomplete
"""\
Type constants for pointers and arrays. Note that there is no explicit
constant for structures, it's implicit: an aggregate type without ``PTR``
or ``ARRAY`` flags is a structure.
"""
ARRAY: Incomplete
"""\
Type constants for pointers and arrays. Note that there is no explicit
constant for structures, it's implicit: an aggregate type without ``PTR``
or ``ARRAY`` flags is a structure.
"""

class struct:
    """
    Module contents
    ---------------
    """

    def __init__(self, addr: int, descriptor: _descriptor, layout_type: int = NATIVE, /) -> None:
        """
        Instantiate a "foreign data structure" object based on structure address in
        memory, descriptor (encoded as a dictionary), and layout type (see below).
        """

def sizeof(struct: struct | _descriptor, layout_type: int = NATIVE, /) -> int:
    """
    Return size of data structure in bytes. The *struct* argument can be
    either a structure class or a specific instantiated structure object
    (or its aggregate field).
    """
    ...

def addressof(obj: AnyReadableBuf, /) -> int:
    """
    Return address of an object. Argument should be bytes, bytearray or
    other object supporting buffer protocol (and address of this buffer
    is what actually returned).
    """
    ...

def bytes_at(addr: int, size: int, /) -> bytes:
    """
    Capture memory at the given address and size as bytes object. As bytes
    object is immutable, memory is actually duplicated and copied into
    bytes object, so if memory contents change later, created object
    retains original value.
    """
    ...

def bytearray_at(addr: int, size: int, /) -> bytearray:
    """
    Capture memory at the given address and size as bytearray object.
    Unlike bytes_at() function above, memory is captured by reference,
    so it can be both written too, and you will access current value
    at the given memory address.
    """
    ...
