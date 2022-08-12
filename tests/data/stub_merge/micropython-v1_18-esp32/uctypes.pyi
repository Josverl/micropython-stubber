from typing import Any

ARRAY: int
BFINT16: int
BFINT32: int
BFINT8: int
BFUINT16: int
BFUINT32: int
BFUINT8: int
BF_LEN: int
BF_POS: int
BIG_ENDIAN: int
FLOAT32: int
FLOAT64: int
INT: int
INT16: int
INT32: int
INT64: int
INT8: int
LITTLE_ENDIAN: int
LONG: int
LONGLONG: int
NATIVE: int
PTR: int
SHORT: int
UINT: int
UINT16: int
UINT32: int
UINT64: int
UINT8: int
ULONG: int
ULONGLONG: int
USHORT: int
VOID: int

def addressof(*args, **kwargs) -> Any: ...
def bytearray_at(*args, **kwargs) -> Any: ...
def bytes_at(*args, **kwargs) -> Any: ...
def sizeof(*args, **kwargs) -> Any: ...

class struct:
    def __init__(self, *argv, **kwargs) -> None: ...
