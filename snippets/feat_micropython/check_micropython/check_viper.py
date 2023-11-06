import micropython
from typing_extensions import TYPE_CHECKING

# https://docs.micropython.org/en/v1.20.0/reference/speed_python.html?highlight=viper#the-viper-code-emitter
# Casting operators are currently: int, bool, uint, ptr, ptr8, ptr16 and ptr32.

# todo: micropython.viper - add support for casting operators in the stubs
if TYPE_CHECKING:
    from array import array
    def ptr(buf: bytes) -> bytearray: ...
    def ptr8(buf: bytes) -> bytearray: ...
    def ptr16(buf: bytes) -> array: ... #Points to a 16 bit half-word.
    def ptr32(buf: bytes) -> array: ... #Points to a 32 bit word.


@micropython.viper
def foo(self, arg: int) -> int:
    ## self.linebuf is a bytearray or bytes object
    buf = ptr8(self.linebuf)
    for x in range(20, 30):
        bar = buf[x]  # Access a data item through the pointer
        # code omitted

    return len(buf)  # Return an integer value
