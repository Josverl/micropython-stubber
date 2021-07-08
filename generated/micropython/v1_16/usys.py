# .. module:: usys
# origin: micropython\docs\library\usys.rst
# v1.16
"""
   :synopsis: system specific functions

|see_cpython_module| :mod:`python:sys`.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: usys
# .. function:: exit(retval=0, /)
def exit(retval=0, /) -> Any:
    """
    Terminate current program with a given exit code. Underlyingly, this
    function raise as `SystemExit` exception. If an argument is given, its
    value given as an argument to `SystemExit`.
    """
    ...


# .. function:: print_exception(exc, file=usys.stdout, /)
def print_exception(exc, file=usys.stdout, /) -> Any:
    """
    Print exception with a traceback to a file-like object *file* (or
    `usys.stdout` by default).

    .. admonition:: Difference to CPython
       :class: attention

       This is simplified version of a function which appears in the
       ``traceback`` module in CPython. Unlike ``traceback.print_exception()``,
       this function takes just exception value instead of exception type,
       exception value, and traceback object; *file* argument should be
       positional; further arguments are not supported. CPython-compatible
       ``traceback`` module can be found in `micropython-lib`.
    """
    ...


# .. data:: argv
# .. data:: byteorder
# .. data:: implementation
# .. data:: maxsize
# .. data:: modules
# .. data:: path
# .. data:: platform
# .. data:: stderr
# .. data:: stdin
# .. data:: stdout
# .. data:: version
# .. data:: version_info
