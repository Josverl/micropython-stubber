# fmt: off
"""
Overloaded method
"""
from typing import overload, Any, Optional

from _typeshed import Incomplete

class Pin:
    ALT_SPI: int = 1
    IN: int = 0
    ALT_USB: int = 9
    ALT_UART: int = 2
    IRQ_FALLING: int = 4
    OUT: int = 1
    OPEN_DRAIN: int = 2
    IRQ_RISING: int = 8
    PULL_DOWN: int = 2
    ALT_SIO: int = 5
    ALT_GPCK: int = 8
    ALT: int = 3
    PULL_UP: int = 1
    ALT_I2C: int = 3
    ALT_PWM: int = 4
    ALT_PIO1: int = 7
    ALT_PIO0: int = 6
    def low(self, *args, **kwargs) -> Incomplete: ...
    def irq(self, *args, **kwargs) -> Incomplete: ...
    def toggle(self, *args, **kwargs) -> Incomplete: ...
    def off(self, *args, **kwargs) -> Incomplete: ...
    def on(self, *args, **kwargs) -> Incomplete: ...
    def init(self, *args, **kwargs) -> Incomplete: ...
    def value(self, *args, **kwargs) -> Incomplete: ...
    def high(self, *args, **kwargs) -> Incomplete: ...

    def foo() -> None: ...
    @overload
    def __call__(self) -> int:
        """
        Pin objects are callable.  The call method provides a (fast) shortcut to set
        and get the value of the pin.  It is equivalent to Pin.value([x]).
        See :meth:`Pin.value` for more details.
        """

    @overload
    def __call__(self, x: Any, /) -> None:
        """
        Pin objects are callable.  The call method provides a (fast) shortcut to set
        and get the value of the pin.  It is equivalent to Pin.value([x]).
        See :meth:`Pin.value` for more details.
        """
    # no def __call__ has been defined in the original file
