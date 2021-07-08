# .. module:: ustruct
# origin: micropython\docs\library\ustruct.rst
# v1.16
"""
   :synopsis: pack and unpack primitive data types

|see_cpython_module| :mod:`python:struct`.

Supported size/byte order prefixes: ``@``, ``<``, ``>``, ``!``.

Supported format codes: ``b``, ``B``, ``h``, ``H``, ``i``, ``I``, ``l``,
``L``, ``q``, ``Q``, ``s``, ``P``, ``f``, ``d`` (the latter 2 depending
on the floating-point support).
"""

from typing import Any, Optional, Union, Tuple

# .. module:: ustruct
# .. function:: calcsize(fmt)
def calcsize(fmt) -> Any:
    """
    Return the number of bytes needed to store the given *fmt*.
    """
    ...


# .. function:: pack_into(fmt, buffer, offset, v1, v2, ...)
def pack_into(fmt, buffer, offset, v1, v2, *args) -> Any:
    """
    Pack the values *v1*, *v2*, ... according to the format string *fmt*
    into a *buffer* starting at *offset*. *offset* may be negative to count
    from the end of *buffer*.
    """
    ...


# .. function:: unpack_from(fmt, data, offset=0, /)
def unpack_from(fmt, data, offset=0, /) -> Any:
    """
    Unpack from the *data* starting at *offset* according to the format string
    *fmt*. *offset* may be negative to count from the end of *buffer*. The return
    value is a tuple of the unpacked values.
    """
    ...
