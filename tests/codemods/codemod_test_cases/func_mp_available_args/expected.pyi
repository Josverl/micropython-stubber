"""
mp_available with arguments

---
Target stub before merge
"""

from _mpy_shed import mp_available

@mp_available("esp32")
def foo(a: int) -> int: ...
@mp_available(["esp32", "rp2"])
def foo(a: str) -> str: ...
