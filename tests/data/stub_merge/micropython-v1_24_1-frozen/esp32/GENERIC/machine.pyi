"""
Module: 'machine' on micropython-v1.24.1-esp32
Frozen complementary extension of the C machine module for ESP32.
Adds port-specific classes not present in the standard C implementation.
"""

# This is a simplified version of the ESP32 frozen machine.py stub.
# It contains classes that extend the C machine module.
# See: https://github.com/micropython/micropython/blob/master/ports/esp32/modules/machine.py

from typing import Any, Optional

# Standard machine classes that also appear in the merged stub (should NOT be duplicated)
class Pin:
    IN: int
    OUT: int

    def __init__(self, id: Any, mode: int = -1, pull: int = -1) -> None: ...
    def value(self, x: Optional[int] = None) -> Optional[int]: ...

# ESP32-specific class: Pulse Counter (PCNT)
# This is the NEW class that the frozen module adds; it is not in the standard machine module.
class PCNT:
    """Pulse Counter peripheral for ESP32."""

    IRQ_ZERO: int
    IRQ_MAX: int
    IRQ_MIN: int

    def __init__(self, unit: int, pin: Any, *, min: int = -32768, max: int = 32767) -> None: ...
    def value(self) -> int: ...
    def irq(self, handler: Any = None, trigger: int = 0) -> None: ...
    def filter_ns(self, ns: int = 0) -> int: ...
