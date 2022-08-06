"""
add from x import y
"""
from functools import lru_cache


@lru_cache
def foo(pin: int, /, limit: int = 100) -> str:
    ...
