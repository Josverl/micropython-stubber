# fmt: off
"""
Reference stub with @mp_available class

---
Target stub before merge - no class exists yet
"""
from _mpy_shed import mp_available

def ticks_ms() -> int: ...

@mp_available()
class _TicksMs:
    """Opaque millisecond tick value. Use ticks_diff() and ticks_add() for operations."""
    def __init__(self, value: int, /) -> None: ...
