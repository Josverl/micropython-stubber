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

        #     .. method:: getvalue()
        class getvalue:
            """ """

            def getvalue(
                self,
            ) -> Any:
                """
                Get the current contents of the underlying buffer which holds data.
                """
                ...

            # .. class:: BytesIO(alloc_size)
            # .. class:: BytesIO(alloc_size)

            # class:: BytesIO
            class BytesIO:
                """
                :noindex:

                Create an empty `StringIO`/`BytesIO` object, preallocated to hold up
                to *alloc_size* number of bytes. That means that writing that amount
                of bytes won't lead to reallocation of the buffer, and thus won't hit
                out-of-memory situation or lead to memory fragmentation. These constructors
                are a MicroPython extension and are recommended for usage only in special
                cases and in system-level libraries, not for end-user applications.

                .. admonition:: Difference to CPython
                    :class: attention

                    These constructors are a MicroPython extension.
                """

                def __init__(self, alloc_size) -> None:
                    ...
