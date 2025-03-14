"""
simple functions 
"""


def foo(x=1, y=2) -> int:
    ...


def foo(x=1, y=2) -> Incomplete:
    ...


def foo(x=1, y=2) -> Any:
    ...


def bar():
    ...
