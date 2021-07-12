from typing import Any, Optional, Union, Tuple

# .. module:: uctypes
# origin: micropython\docs\library\uctypes.rst
# v1.16
"""
   :synopsis: access binary data in a structured way

This module implements "foreign data interface" for MicroPython. The idea
behind it is similar to CPython's ``ctypes`` modules, but the actual API is
different, streamlined and optimized for small size. The basic idea of the
module is to define data structure layout with about the same power as the
C language allows, and then access it using familiar dot-syntax to reference
sub-fields.
"""
# .. warning::
# .. seealso::
# .. class:: struct(addr, descriptor, layout_type=NATIVE, /)
# class:: struct
class struct:
    """
    Instantiate a "foreign data structure" object based on structure address in
    memory, descriptor (encoded as a dictionary), and layout type (see below).
    """

    def __init__(self, addr, descriptor, layout_type=NATIVE, /) -> None:
        ...


# .. data:: LITTLE_ENDIAN
# .. data:: BIG_ENDIAN
# .. data:: NATIVE
# .. function:: sizeof(struct, layout_type=NATIVE, /)
def sizeof(struct, layout_type=NATIVE, /) -> Any:
    """
    Return size of data structure in bytes. The *struct* argument can be
    either a structure class or a specific instantiated structure object
    (or its aggregate field).
    """
    ...


# .. function:: addressof(obj)
def addressof(obj) -> Any:
    """
    Return address of an object. Argument should be bytes, bytearray or
    other object supporting buffer protocol (and address of this buffer
    is what actually returned).
    """
    ...


# .. function:: bytes_at(addr, size)
def bytes_at(addr, size) -> Any:
    """
    Capture memory at the given address and size as bytes object. As bytes
    object is immutable, memory is actually duplicated and copied into
    bytes object, so if memory contents change later, created object
    retains original value.
    """
    ...


# .. function:: bytearray_at(addr, size)
def bytearray_at(addr, size) -> Any:
    """
    Capture memory at the given address and size as bytearray object.
    Unlike bytes_at() function above, memory is captured by reference,
    so it can be both written too, and you will access current value
    at the given memory address.
    """
    ...


# .. data:: UINT8
# .. data:: FLOAT32
# .. data:: VOID
# .. data:: PTR
