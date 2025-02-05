""" """

from __future__ import annotations

from machine import IDLE
from machine.ADC import ADC
from machine.ADCBlock import ADCBlock
from machine.I2C import I2C
from machine.I2S import I2S
from machine.Pin import Pin
from machine.PWM import PWM
from machine.RTC import RTC
from machine.SD import SD
from machine.SDCard import SDCard
from machine.Signal import Signal
from machine.SPI import SPI
from machine.Timer import Timer
from machine.UART import UART
from machine.USBDevice import USBDevice
from machine.WDT import WDT

from .Pin import Pin

class SD:
    """
    .. warning::

       This is a non-standard class and is only available on the cc3200 port.


    The SD card class allows to configure and enable the memory card
    module of the WiPy and automatically mount it as ``/sd`` as part
    of the file system. There are several pin combinations that can be
    used to wire the SD card socket to the WiPy and the pins used can
    be specified in the constructor. Please check the `pinout and alternate functions
    table. <https://raw.githubusercontent.com/wipy/wipy/master/docs/PinOUT.png>`_ for
    more info regarding the pins which can be remapped to be used with a SD card.

    Example usage::

        from machine import SD
        import os
        # clk cmd and dat0 pins must be passed along with
        # their respective alternate functions
        sd = machine.SD(pins=('GP10', 'GP11', 'GP15'))
        os.mount(sd, '/sd')
        # do normal file operations
    """

    def __init__(
        self,
        id: int = 0,
        pins: tuple[str, str, str] | tuple[Pin, Pin, Pin] = ("GP10", "GP11", "GP15"),
        /,
    ) -> None:
        """
        Create a SD card object. See ``init()`` for parameters if initialization.
        """

    def init(
        self,
        id: int = 0,
        pins: tuple[str, str, str] | tuple[Pin, Pin, Pin] = ("GP10", "GP11", "GP15"),
        /,
    ) -> None:
        """
        Enable the SD card. In order to initialize the card, give it a 3-tuple:
        ``(clk_pin, cmd_pin, dat0_pin)``.
        """
        ...

    def deinit(self) -> None:
        """
        Disable the SD card.
        """
        ...
