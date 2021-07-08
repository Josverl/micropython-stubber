# .. module:: gc
# origin: micropython\docs\library\gc.rst
# v1.16
"""
   :synopsis: control the garbage collector

|see_cpython_module| :mod:`python:gc`.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: gc
# .. function:: enable()
def enable() -> Any:
    """
    Enable automatic garbage collection.
    """
    ...


# .. function:: collect()
def collect() -> Any:
    """
    Run a garbage collection.
    """
    ...


# .. function:: mem_free()
def mem_free() -> Any:
    """
    Return the number of bytes of available heap RAM, or -1 if this amount
    is not known.

    .. admonition:: Difference to CPython
       :class: attention

       This function is MicroPython extension.
    """
    ...
