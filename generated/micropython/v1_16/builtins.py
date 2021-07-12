from typing import Any, Optional, Union, Tuple

# .. function:: abs()
def abs() -> Any:
    """
    """
    ...


# .. function:: all()
def all() -> Any:
    """
    """
    ...


# .. function:: any()
def any() -> Any:
    """
    """
    ...


# .. function:: bin()
def bin() -> Any:
    """
    """
    ...


# .. class:: bool()
# class:: bool
class bool:
    """
    """
    def __init__(self, ) -> None:
        ...

# .. class:: bytearray()
# class:: bytearray
class bytearray:
    """
    """
    def __init__(self, ) -> None:
        ...

# .. class:: bytes()
# class:: bytes
class bytes:
    """
        |see_cpython| `python:bytes`.
    """
    def __init__(self, ) -> None:
        ...

# .. function:: callable()
def callable() -> Any:
    """
    """
    ...


# .. function:: chr()
def chr() -> Any:
    """
    """
    ...


# .. function:: classmethod()
def classmethod() -> Any:
    """
    """
    ...


# .. function:: compile()
def compile() -> Any:
    """
    """
    ...


# .. class:: complex()
# class:: complex
class complex:
    """
    """
    def __init__(self, ) -> None:
        ...

# .. function:: delattr(obj, name)
def delattr(obj, name) -> Any:
    """
       The argument *name* should be a string, and this function deletes the named
       attribute from the object given by *obj*.
    """
    ...


# .. class:: dict()
# class:: dict
class dict:
    """
    """
    def __init__(self, ) -> None:
        ...

# .. function:: dir()
def dir() -> Any:
    """
    """
    ...


# .. function:: divmod()
def divmod() -> Any:
    """
    """
    ...


# .. function:: enumerate()
def enumerate() -> Any:
    """
    """
    ...


# .. function:: eval()
def eval() -> Any:
    """
    """
    ...


# .. function:: exec()
def exec() -> Any:
    """
    """
    ...


# .. function:: filter()
def filter() -> Any:
    """
    """
    ...


# .. class:: float()
# class:: float
class float:
    """
    """
    def __init__(self, ) -> None:
        ...

# .. class:: frozenset()
# class:: frozenset
class frozenset:
    """
    """
    def __init__(self, ) -> None:
        ...

# .. function:: getattr()
def getattr() -> Any:
    """
    """
    ...


# .. function:: globals()
def globals() -> Any:
    """
    """
    ...


# .. function:: hasattr()
def hasattr() -> Any:
    """
    """
    ...


# .. function:: hash()
def hash() -> Any:
    """
    """
    ...


# .. function:: hex()
def hex() -> Any:
    """
    """
    ...


# .. function:: id()
def id() -> Any:
    """
    """
    ...


# .. function:: input()
def input() -> Any:
    """
    """
    ...


# .. class:: int()
# class:: int
class int:
    """
    """
    def __init__(self, ) -> None:
        ...

#    .. classmethod:: from_bytes(bytes, byteorder)
    @classmethod
    def from_bytes(cls, bytes, byteorder) -> Any:
        """
              In MicroPython, `byteorder` parameter must be positional (this is
              compatible with CPython).
        """
        ...

#    .. method:: to_bytes(size, byteorder)
    def to_bytes(self, size, byteorder) -> Any:
        """
              In MicroPython, `byteorder` parameter must be positional (this is
              compatible with CPython).
        """
        ...

# .. function:: isinstance()
def isinstance() -> Any:
    """
    """
    ...


# .. function:: issubclass()
def issubclass() -> Any:
    """
    """
    ...


# .. function:: iter()
def iter() -> Any:
    """
    """
    ...


# .. function:: len()
def len() -> Any:
    """
    """
    ...


# .. class:: list()
# class:: list
class list:
    """
    """
    def __init__(self, ) -> None:
        ...

# .. function:: locals()
def locals() -> Any:
    """
    """
    ...


# .. function:: map()
def map() -> Any:
    """
    """
    ...


# .. function:: max()
def max() -> Any:
    """
    """
    ...


# .. class:: memoryview()
# class:: memoryview
class memoryview:
    """
    """
    def __init__(self, ) -> None:
        ...

# .. function:: min()
def min() -> Any:
    """
    """
    ...


# .. function:: next()
def next() -> Any:
    """
    """
    ...


# .. class:: object()
# class:: object
class object:
    """
    """
    def __init__(self, ) -> None:
        ...

# .. function:: oct()
def oct() -> Any:
    """
    """
    ...


# .. function:: open()
def open() -> Any:
    """
    """
    ...


# .. function:: ord()
def ord() -> Any:
    """
    """
    ...


# .. function:: pow()
def pow() -> Any:
    """
    """
    ...


# .. function:: print()
def print() -> Any:
    """
    """
    ...


# .. function:: property()
def property() -> Any:
    """
    """
    ...


# .. function:: range()
def range() -> Any:
    """
    """
    ...


# .. function:: repr()
def repr() -> Any:
    """
    """
    ...


# .. function:: reversed()
def reversed() -> Any:
    """
    """
    ...


# .. function:: round()
def round() -> Any:
    """
    """
    ...


# .. class:: set()
# class:: set
class set:
    """
    """
    def __init__(self, ) -> None:
        ...

# .. function:: setattr()
def setattr() -> Any:
    """
    """
    ...


# .. class:: slice()
# class:: slice
class slice:
    """
       The *slice* builtin is the type that slice objects have.
    """
    def __init__(self, ) -> None:
        ...

# .. function:: sorted()
def sorted() -> Any:
    """
    """
    ...


# .. function:: staticmethod()
def staticmethod() -> Any:
    """
    """
    ...


# .. class:: str()
# class:: str
class str:
    """
    """
    def __init__(self, ) -> None:
        ...

# .. function:: sum()
def sum() -> Any:
    """
    """
    ...


# .. function:: super()
def super() -> Any:
    """
    """
    ...


# .. class:: tuple()
# class:: tuple
class tuple:
    """
    """
    def __init__(self, ) -> None:
        ...

# .. function:: type()
def type() -> Any:
    """
    """
    ...


# .. function:: zip()
def zip() -> Any:
    """
    """
    ...


# .. exception:: AssertionError
# .. exception:: AttributeError
# .. exception:: Exception
# .. exception:: ImportError
# .. exception:: IndexError
# .. exception:: KeyboardInterrupt
# .. exception:: KeyError
# .. exception:: MemoryError
# .. exception:: NameError
# .. exception:: NotImplementedError
# .. exception:: OSError
# .. exception:: RuntimeError
# .. exception:: StopIteration
# .. exception:: SyntaxError
# .. exception:: SystemExit
# .. exception:: TypeError
# .. exception:: ValueError
# .. exception:: ZeroDivisionError
