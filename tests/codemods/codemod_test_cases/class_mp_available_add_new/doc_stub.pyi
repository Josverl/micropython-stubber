# fmt: off
"""
Reference stub with @mp_available class
"""

from _mpy_shed import mp_available

@mp_available()
class _TicksMs:
    """Opaque millisecond tick value. Use ticks_diff() and ticks_add() for operations."""
    def __init__(self, value: int, /) -> None: ...

def ticks_ms() -> _TicksMs: ...
