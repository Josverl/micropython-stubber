"""
Module: 'machine' on micropython-linux-1.16
"""
# MCU: {'ver': '1.16', 'port': 'linux', 'arch': 'x64', 'sysname': 'unknown', 'release': '1.16.0', 'name': 'micropython', 'mpy': 2821, 'version': '1.16.0', 'machine': 'unknown', 'build': '', 'nodename': 'unknown', 'platform': 'linux', 'family': 'micropython'}
# Stubber: 1.3.16
from typing import Any


class PinBase:
    """"""


class Signal:
    """"""

    def value(self, *args) -> Any:
        """"""
        ...

    def off(self, *args) -> Any:
        """"""
        ...

    def on(self, *args) -> Any:
        """"""
        ...


def idle(self, *args) -> Any:
    """"""
    ...


mem16 = int  # <16-bit memory> # type: mem
mem32 = int  # <32-bit memory> # type: mem
mem8 = int  # <8-bit memory> # type: mem


def time_pulse_us(self, *args) -> Any:
    """"""
    ...
