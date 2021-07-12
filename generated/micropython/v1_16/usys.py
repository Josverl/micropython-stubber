from typing import Any, Optional, Union, Tuple

# .. module:: usys
# origin: micropython\docs\library\usys.rst
# v1.16
"""
   :synopsis: system specific functions

|see_cpython_module| :mod:`python:sys`.
"""
# .. function:: exit(retval=0, /)
def exit(retval=0, /) -> Any:
    """
    Terminate current program with a given exit code. Underlyingly, this
    function raise as `SystemExit` exception. If an argument is given, its
    value given as an argument to `SystemExit`.
    """
    ...


# .. function:: atexit(func)
def atexit(func) -> Any:
    """
    Register *func* to be called upon termination.  *func* must be a callable
    that takes no arguments, or ``None`` to disable the call.  The ``atexit``
    function will return the previous value set by this function, which is
    initially ``None``.
    """
    ...


#    .. admonition:: Difference to CPython
# .. function:: print_exception(exc, file=usys.stdout, /)
def print_exception(exc, file=usys.stdout, /) -> Any:
    """
    Print exception with a traceback to a file-like object *file* (or
    `usys.stdout` by default).
    """
    ...


#    .. admonition:: Difference to CPython
# .. data:: argv
# .. data:: byteorder
# .. data:: implementation
#    .. admonition:: Difference to CPython
# .. data:: maxsize
# .. data:: modules
# .. data:: path
# .. data:: platform
# .. data:: stderr
# .. data:: stdin
# .. data:: stdout
# .. data:: version
# .. data:: version_info
#     .. admonition:: Difference to CPython
