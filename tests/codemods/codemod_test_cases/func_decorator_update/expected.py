"""
simple functions 
"""

def bar(f):
    ...


@lru_cache
@bar
def foo(pin: int, /, limit: int = 100) -> str:
    ...
