"""
simple functions 
"""

@foo
def foo(pin: int, /, limit: int = 100) -> str: ...


@lru_cache
def foo(pin: int, /, limit: int = 100) -> str: ...
