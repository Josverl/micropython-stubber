# .. module:: uio
# origin: micropython\docs\library\uio.rst
# v1.16
"""
   :synopsis: input/output streams

|see_cpython_module| :mod:`python:io`.

This module contains additional types of `stream` (file-like) objects
and helper functions.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: uio
# .. admonition:: Difference to CPython
# .. function:: open(name, mode='r', **kwargs)
def open(name, mode="r", **kwargs) -> Any:
    """
    Open a file. Builtin ``open()`` function is aliased to this function.
    All ports (which provide access to file system) are required to support
    *mode* parameter, but support for other arguments vary by port.
    """
    ...


# .. class:: FileIO(...)
# .. class:: FileIO(...)

# class:: FileIO
class FileIO:
    """
    This is type of a file open in binary mode, e.g. using ``open(name, "rb")``.
    You should not instantiate this class directly.
    """

    def __init__(self, *args) -> None:
        ...

    # .. class:: StringIO([string])
    # .. class:: StringIO([string])

    # class:: StringIO
    class StringIO:
        """ """

        def __init__(self, string: Optional[Any]) -> None:
            ...

        # .. class:: StringIO(alloc_size)
        # .. class:: StringIO(alloc_size)

        # class:: StringIO
        class StringIO:
            """
            :noindex:
            """

            def __init__(self, alloc_size) -> None:
                ...
