# .. module:: ubinascii
# origin: micropython\docs\library\ubinascii.rst
# v1.16
"""
   :synopsis: binary/ASCII conversions

|see_cpython_module| :mod:`python:binascii`.

This module implements conversions between binary data and various
encodings of it in ASCII form (in both directions).
"""

from typing import Any, Optional, Union, Tuple

# .. module:: ubinascii
# .. function:: hexlify(data, [sep])
def hexlify(data, sep: Optional[Any]) -> Any:
    """
    Convert the bytes in the *data* object to a hexadecimal representation.
    Returns a bytes object.

    If the additional argument *sep* is supplied it is used as a separator
    between hexadecimal values.
    """
    ...


# .. function:: a2b_base64(data)
def a2b_base64(data) -> Any:
    """
    Decode base64-encoded data, ignoring invalid characters in the input.
    Conforms to `RFC 2045 s.6.8 <https://tools.ietf.org/html/rfc2045#section-6.8>`_.
    Returns a bytes object.
    """
    ...
