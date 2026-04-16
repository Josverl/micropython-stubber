# fmt: off
"""
Reference stub with multiple @mp_available classes
"""

from typing_extensions import TypeVar

from _mpy_shed import mp_available

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

_Ticks = TypeVar("_Ticks", _TicksMs, _TicksUs, _TicksCPU)

def ticks_ms() -> _TicksMs: ...
def ticks_us() -> _TicksUs: ...
def ticks_cpu() -> _TicksCPU: ...
