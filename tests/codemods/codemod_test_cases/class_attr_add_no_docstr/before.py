# fmt: off
"""
add attribute
"""

class Foo:
    EXISTING = "Do not overwrite me"

    def foo(): ...


    def bar(): ...


class UART:
    INV_TX: int = 1
    RTS: int = 2
    INV_RX: int = 2
    IRQ_TXIDLE: int = 32
    IRQ_BREAK: int = 512
    IRQ_RXIDLE: int = 64
    CTS: int = 1

    def irq(
        self,
        trigger: int,
        priority: int = 1,
        handler: Callable[[UART], None] | None = None,
        wake: int = IDLE,
        /,
    ) -> _IRQ: ...
