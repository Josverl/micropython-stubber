# .. module:: micropython
# origin: micropython\docs\library\micropython.rst
# v1.16
"""
   :synopsis: access and control MicroPython internals
"""

from typing import Any, Optional, Union, Tuple

# .. module:: micropython
# .. function:: const(expr)
def const(expr) -> Any:
    """
    Used to declare that the expression is a constant so that the compile can
    optimise it.  The use of this function should be as follows::

     from micropython import const

     CONST_X = const(123)
     CONST_Y = const(2 * CONST_X + 1)

    Constants declared this way are still accessible as global variables from
    outside the module they are declared in.  On the other hand, if a constant
    begins with an underscore then it is hidden, it is not available as a global
    variable, and does not take up any memory during execution.

    This `const` function is recognised directly by the MicroPython parser and is
    provided as part of the :mod:`micropython` module mainly so that scripts can be
    written which run under both CPython and MicroPython, by following the above
    pattern.
    """
    ...


# .. function:: alloc_emergency_exception_buf(size)
def alloc_emergency_exception_buf(size) -> Any:
    """
    Allocate *size* bytes of RAM for the emergency exception buffer (a good
    size is around 100 bytes).  The buffer is used to create exceptions in cases
    when normal RAM allocation would fail (eg within an interrupt handler) and
    therefore give useful traceback information in these situations.

    A good way to use this function is to put it at the start of your main script
    (eg ``boot.py`` or ``main.py``) and then the emergency exception buffer will be active
    for all the code following it.
    """
    ...


# .. function:: qstr_info([verbose])
def qstr_info(verbose: Optional[Any]) -> Any:
    """
    Print information about currently interned strings.  If the *verbose*
    argument is given then extra information is printed.

    The information that is printed is implementation dependent, but currently
    includes the number of interned strings and the amount of RAM they use.  In
    verbose mode it prints out the names of all RAM-interned strings.
    """
    ...


# .. function:: heap_lock()
def heap_lock() -> Any:
    """ """
    ...


# .. function:: kbd_intr(chr)
def kbd_intr(chr) -> Any:
    """
    Set the character that will raise a `KeyboardInterrupt` exception.  By
    default this is set to 3 during script execution, corresponding to Ctrl-C.
    Passing -1 to this function will disable capture of Ctrl-C, and passing 3
    will restore it.

    This function can be used to prevent the capturing of Ctrl-C on the
    incoming stream of characters that is usually used for the REPL, in case
    that stream is used for other purposes.
    """
    ...
