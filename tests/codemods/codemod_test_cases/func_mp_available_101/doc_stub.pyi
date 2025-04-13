"""
Overloaded functions from python docs
"""

from _mpy_shed import mp_available

@mp_available
def process(response: None) -> None: ...
@mp_available
def process(response: int) -> tuple[int, str]: ...
@mp_available
def process(response: bytes) -> str: ...
