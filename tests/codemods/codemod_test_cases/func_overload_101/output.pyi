# fmt: off
"""
Overloaded functions from python docs
"""
from typing import overload


@overload
def process(response: None) -> None: ...
@overload
def process(response: int) -> tuple[int, str]: ...
@overload
def process(response: bytes) -> str: ...
