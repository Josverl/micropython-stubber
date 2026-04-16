# fmt: off
"""
Reference stub with multiple @mp_available classes

---
Target stub before merge - no tick classes
"""
from _mpy_shed import mp_available
from typing_extensions import TypeVar

_Ticks = TypeVar("_Ticks", _TicksMs, _TicksUs, _TicksCPU)

def ticks_ms() -> int: ...
def ticks_us() -> int: ...
def ticks_cpu() -> int: ...

@mp_available()
class _TicksMs:
    """Opaque millisecond tick value."""
    def __init__(self, value: int, /) -> None: ...

@mp_available()
class _TicksUs:
    """Opaque microsecond tick value."""
    def __init__(self, value: int, /) -> None: ...

@mp_available()
class _TicksCPU:
    """Opaque CPU tick value."""
    def __init__(self, value: int, /) -> None: ...
