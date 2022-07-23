"""
Code snippet used to validate the micropython stubs

module: Micropython 

Validation based on the pycopy stubs, which are incomplete.
"""

# const
import micropython
from micropython import const

ROWS = const(33)
_COLS = const(0x10)
a = ROWS
b = _COLS


@micropython.viper
def foo(arg: int) -> int:
    return arg << 2


@micropython.native
def bar(arg: int) -> int:
    return arg << 2


micropython.mem_free()
micropython.mem_alloc()


##########################################
# below functions are not supported yet ##
##########################################

x = micropython.opt_level()  # type: ignore # FIXME
micropython.opt_level(x)  # type: ignore # FIXME


micropython.alloc_emergency_exception_buf(512)  # type: ignore # FIXME

micropython.mem_info()  # type: ignore # FIXME
micropython.qstr_info()  # type: ignore # FIXME
micropython.stack_use()  # type: ignore # FIXME
micropython.heap_lock()  # type: ignore # FIXME
micropython.heap_unlock()  # type: ignore # FIXME
micropython.heap_locked()  # type: ignore # FIXME


micropython.kbd_intr()  # type: ignore # FIXME


# supply params to the function
def func(a):
    print(a)


arg = "foo"

micropython.schedule(func, arg)  # type: ignore # FIXME
