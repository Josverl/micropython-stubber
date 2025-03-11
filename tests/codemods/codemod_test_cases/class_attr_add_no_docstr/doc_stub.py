# fmt: off
"""
add attribute
"""
from typing import Final


class Foo:
    ATTRIBUTE = True  # available 
    """the important docstring"""

    TYPED:bool = ...  # available 
    """the important docstring"""

    ignored  = 42  # available 
    """the important docstring"""

    FINAL = Final(42)  # available
    """the important docstring"""

    IS_OK = const(32)  # available

    EXISTING = "Should not overwrite existing"

    def foo(): ...



class UART:
    INV_TX: int = 1
    RTS: int = 2
    INV_RX: int = 2
    IRQ_TXIDLE: int = 32
    IRQ_BREAK: int = 512
    IRQ_RXIDLE: int = 64
    CTS: int = 1
    IDLE : int = ...

    def irq(
        self,
        trigger: int,
        priority: int = 1,
        handler: Callable[[UART], None] | None = None,
        wake: int = IDLE,
        /,
    ) -> _IRQ: ...

    
        