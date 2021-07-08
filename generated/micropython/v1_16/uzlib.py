# .. module:: uzlib
# origin: micropython\docs\library\uzlib.rst
# v1.16
"""
   :synopsis: zlib decompression

|see_cpython_module| :mod:`python:zlib`.

This module allows to decompress binary data compressed with
`DEFLATE algorithm <https://en.wikipedia.org/wiki/DEFLATE>`_
(commonly used in zlib library and gzip archiver). Compression
is not yet implemented.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: uzlib
# .. function:: decompress(data, wbits=0, bufsize=0, /)
def decompress(data, wbits=0, bufsize=0, /) -> Any:
    """
    Return decompressed *data* as bytes. *wbits* is DEFLATE dictionary window
    size used during compression (8-15, the dictionary size is power of 2 of
    that value). Additionally, if value is positive, *data* is assumed to be
    zlib stream (with zlib header). Otherwise, if it's negative, it's assumed
    to be raw DEFLATE stream. *bufsize* parameter is for compatibility with
    CPython and is ignored.
    """
    ...
