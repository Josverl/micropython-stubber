from typing import Any, Dict, Optional, Sequence, Tuple, Union

Node = Any

def sleep_ms(t: Any) -> None: ...
def sleep_us(t: Any) -> None: ...
def ticks_ms() -> Any: ...

#   0: return int(_time.time()*)&MICROPY_PY_UTIME_TICKS_PERIOD-
# ? 0: return int&MICROPY_PY_UTIME_TICKS_PERIOD-
def ticks_us() -> Any: ...

#   0: return int(_time.time()*)&MICROPY_PY_UTIME_TICKS_PERIOD-
# ? 0: return int&MICROPY_PY_UTIME_TICKS_PERIOD-
def ticks_add(t: Any, delta: Any) -> Any: ...

#   0: return t+delta&MICROPY_PY_UTIME_TICKS_PERIOD-
# ? 0: return t+delta&MICROPY_PY_UTIME_TICKS_PERIOD-
def ticks_diff(a: str, b: Any) -> Any: ...

#   0: return a-b+MICROPY_PY_UTIME_TICKS_PERIOD//&MICROPY_PY_UTIME_TICKS_PERIOD--MICROPY_PY_UTIME_TICKS_PERIOD//
# ? 0: return str-b+MICROPY_PY_UTIME_TICKS_PERIOD//&MICROPY_PY_UTIME_TICKS_PERIOD--MICROPY_PY_UTIME_TICKS_PERIOD//
