"""
Deflate compression & decompression.

MicroPython module: https://docs.micropython.org/en/v1.24.0/library/deflate.html

This module allows compression and decompression of binary data with the
`DEFLATE algorithm <https://en.wikipedia.org/wiki/DEFLATE>`_
(commonly used in the zlib library and gzip archiver).

**Availability:**

* Added in MicroPython v1.21.

* Decompression: Enabled via the ``MICROPY_PY_DEFLATE`` build option, on by default
  on ports with the "extra features" level or higher (which is most boards).

* Compression: Enabled via the ``MICROPY_PY_DEFLATE_COMPRESS`` build option, on
  by default on ports with the "full features" level or higher (generally this means
  you need to build your own firmware to enable this).
"""

# source version: v1.24.1
# origin module:: repos/micropython/docs/library/deflate.rst
from __future__ import annotations

from _typeshed import Incomplete

AUTO: Incomplete
"""Supported values for the *format* parameter."""
RAW: Incomplete
"""Supported values for the *format* parameter."""
ZLIB: Incomplete
"""Supported values for the *format* parameter."""
GZIP: Incomplete
"""Supported values for the *format* parameter."""

class DeflateIO:
    """
    This class can be used to wrap a *stream* which is any
    :term:`stream-like <stream>` object such as a file, socket, or stream
    (including :class:`io.BytesIO`). It is itself a stream and implements the
    standard read/readinto/write/close methods.

    The *stream* must be a blocking stream. Non-blocking streams are currently
    not supported.

    The *format* can be set to any of the constants defined below, and defaults
    to ``AUTO`` which for decompressing will auto-detect gzip or zlib streams,
    and for compressing it will generate a raw stream.

    The *wbits* parameter sets the base-2 logarithm of the DEFLATE dictionary
    window size. So for example, setting *wbits* to ``10`` sets the window size
    to 1024 bytes. Valid values are ``5`` to ``15`` inclusive (corresponding to
    window sizes of 32 to 32k bytes).

    If *wbits* is set to ``0`` (the default), then for compression a window size
    of 256 bytes will be used (as if *wbits* was set to 8). For decompression, it
    depends on the format:

    * ``RAW`` will use 256 bytes (corresponding to *wbits* set to 8).
    * ``ZLIB`` (or ``AUTO`` with zlib detected) will use the value from the zlib
      header.
    * ``GZIP`` (or ``AUTO`` with gzip detected) will use 32 kilobytes
      (corresponding to *wbits* set to 15).

    See the :ref:`window size <deflate_wbits>` notes below for more information
    about the window size, zlib, and gzip streams.

    If *close* is set to ``True`` then the underlying stream will be closed
    automatically when the :class:`deflate.DeflateIO` stream is closed. This is
    useful if you want to return a :class:`deflate.DeflateIO` stream that wraps
    another stream and not have the caller need to know about managing the
    underlying stream.

    If compression is enabled, a given :class:`deflate.DeflateIO` instance
    supports both reading and writing. For example, a bidirectional stream like
    a socket can be wrapped, which allows for compression/decompression in both
    directions.
    """

    def __init__(self, stream, format=AUTO, wbits=0, close=False, /) -> None: ...
