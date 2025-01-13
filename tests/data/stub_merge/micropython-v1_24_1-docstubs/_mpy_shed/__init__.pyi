"""
MicroPython-stubs base types that are not present in typeshed.

This is a collection of types that are not present in typeshed, but are used in the micropython stubs.

Common cases are:
- MicroPython implementation is different from CPython, so the types are different.
- MicroPython has some types that are not present in CPython.

"""

from __future__ import annotations

import abc  # type: ignore - not collections.abc
import sys
from array import array
from typing import Final, final

from _typeshed import structseq
from typing_extensions import TypeAlias, TypeVar

from .subscriptable import Subscriptable as Subscriptable
from .IRQs import _IRQ
from .NeoPixelBase import _NeoPixelBase as _NeoPixelBase
from blockdevice import AbstractBlockDev as AbstractBlockDev, _OldAbstractBlockDev, _OldAbstractReadOnlyBlockDev

from .io_mp import (
    BytesIO as BytesIO,
    FileIO as FileIO,
    IncrementalNewlineDecoder as IncrementalNewlineDecoder,
    StringIO as StringIO,
    TextIOWrapper as TextIOWrapper,
    IOBase as IOBase,
    _BufferedIOBase,
    _IOBase,
    _RawIOBase,
    _TextIOBase,
    open as open,
)
from .pathlike import PathLike

# ------------------
# copied from _typeshed  os.pyi as os.pyi cannot import from a module with the same name
GenericAlias = type(list[int])

# ------------------------------------------------------------------------------------
AnyReadableBuf: TypeAlias = bytearray | array | memoryview | bytes
AnyWritableBuf: TypeAlias = bytearray | array | memoryview

# ------------------------------------------------------------------------------------
StrOrBytesPath: TypeAlias = str | bytes | PathLike[str] | PathLike[bytes]
_StrOrBytesT = TypeVar("_StrOrBytesT", str, bytes)

# ------------------------------------------------------------------------------------
_AnyPath: TypeAlias = str | bytes | PathLike[str] | PathLike[bytes]
_FdOrAnyPath: TypeAlias = int | _AnyPath

# ------------------------------------------------------------------------------------
# HID_Tuple is used in multiple pyb.submodules
HID_Tuple: TypeAlias = tuple[int, int, int, int, bytes]

#  ------------------------------------------------------------------------------------
# copied from _typeshed  os.pyi as os.pyi cannot import from a module with the same nam@final
@final
class uname_result(structseq[str], tuple[str, str, str, str, str]):
    if sys.version_info >= (3, 8):
        __match_args__: Final = ("sysname", "nodename", "release", "version", "machine")

    @property
    def sysname(self) -> str: ...
    @property
    def nodename(self) -> str: ...
    @property
    def release(self) -> str: ...
    @property
    def version(self) -> str: ...
    @property
    def machine(self) -> str: ...

# ------------------------------------------------------------------------------------

###########################
# HashLib

# manual addition to hashlib.pyi

class _Hash(abc.ABC):
    """
    Abstract base class for hashing algorithms that defines methods available in all algorithms.
    """

    def update(self, data: AnyReadableBuf, /) -> None:
        """
        Feed more binary data into hash.
        """

    def digest(self) -> bytes:
        """
        Return hash for all data passed through hash, as a bytes object. After this
        method is called, more data cannot be fed into the hash any longer.
        """

    def hexdigest(self) -> str:
        """
        This method is NOT implemented. Use ``binascii.hexlify(hash.digest())``
        to achieve a similar effect.
        """
