# fmt: off
"""
Reference stub with @mp_available class

---
Target stub already has the @mp_available class
"""

from _mpy_shed import mp_available

def ticks_ms() -> _TicksMs: ...
@mp_available()
class _TicksMs:
    """Opaque millisecond tick value. Use ticks_diff() and ticks_add() for operations."""
    def __init__(self, value: int, /) -> None: ...
