from typing import Any, Dict, Optional, Sequence, Tuple, Union

Node = Any

class UioStream:
    def __init__(self, s: str, is_bin: Any) -> None: ...
    def write(self, data: Any, off: Any = None, sz: Any = None) -> None: ...
    def __getattr__(self, attr: Any) -> Any: ...
    #   0: return getattr(self._s,attr)
    # ? 0: return getattr(self._s, attr)
    def __enter__(self) -> Any: ...
    #   0: return self
    # ? 0: return self
    def __exit__(self, *args) -> Any: ...
    #   0: return self._s.__exit__(*args)
    # ? 0: return self._s.__exit__(*args)

def open(name: str, mode: Any = "r", *args, **kw) -> Any: ...

#   0: return UioStream(f,'b' in mode)
# ? 0: return UioStream(f, bool)
