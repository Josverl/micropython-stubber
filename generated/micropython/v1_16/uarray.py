from typing import Any, Optional, Union, Tuple

# .. module:: uarray
# origin: micropython\docs\library\uarray.rst
# v1.16
"""
   :synopsis: efficient arrays of numeric data

|see_cpython_module| :mod:`python:array`.

Supported format codes: ``b``, ``B``, ``h``, ``H``, ``i``, ``I``, ``l``,
``L``, ``q``, ``Q``, ``f``, ``d`` (the latter 2 depending on the
floating-point support).
"""
# .. class:: array(typecode, [iterable])
# class:: array
class array:
    """
    Create array with elements of given type. Initial contents of the
    array are given by *iterable*. If it is not provided, an empty
    array is created.
    """

    def __init__(self, typecode, iterable: Optional[Any]) -> None:
        ...

    #     .. method:: append(val)
    def append(self, val) -> Any:
        """
        Append new element *val* to the end of array, growing it.
        """
        ...

    #     .. method:: extend(iterable)
    def extend(self, iterable) -> Any:
        """
        Append new elements as contained in *iterable* to the end of
        array, growing it.
        """
        ...
