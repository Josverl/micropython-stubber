""" """

from __future__ import annotations

from array import array
from collections.abc import Sequence
from typing import overload

from _mpy_shed import AnyWritableBuf
from pyb.Accel import Accel
from pyb.ADC import ADC
from pyb.CAN import CAN
from pyb.DAC import DAC
from pyb.ExtInt import ExtInt
from pyb.Flash import Flash
from pyb.I2C import I2C
from pyb.LCD import LCD
from pyb.LED import LED
from pyb.Pin import Pin
from pyb.RTC import RTC
from pyb.Servo import Servo
from pyb.SPI import SPI
from pyb.Switch import Switch
from pyb.Timer import Timer
from pyb.UART import UART
from pyb.USB_HID import USB_HID
from pyb.USB_VCP import USB_VCP

class USB_HID:
    """
    The USB_HID class allows creation of an object representing the USB
    Human Interface Device (HID) interface.  It can be used to emulate
    a peripheral such as a mouse or keyboard.

    Before you can use this class, you need to use :meth:`pyb.usb_mode()` to set the USB mode to include the HID interface.
    """

    def __init__(self) -> None:
        """
        Create a new USB_HID object.
        """

    @overload
    def recv(self, data: int, /, *, timeout: int = 5000) -> bytes:
        """
        Receive data on the bus:

          - ``data`` can be an integer, which is the number of bytes to receive,
            or a mutable buffer, which will be filled with received bytes.
          - ``timeout`` is the timeout in milliseconds to wait for the receive.

        Return value: if ``data`` is an integer then a new buffer of the bytes received,
        otherwise the number of bytes read into ``data`` is returned.
        """

    @overload
    def recv(self, data: AnyWritableBuf, /, *, timeout: int = 5000) -> int:
        """
        Receive data on the bus:

          - ``data`` can be an integer, which is the number of bytes to receive,
            or a mutable buffer, which will be filled with received bytes.
          - ``timeout`` is the timeout in milliseconds to wait for the receive.

        Return value: if ``data`` is an integer then a new buffer of the bytes received,
        otherwise the number of bytes read into ``data`` is returned.
        """

    def send(self, data: Sequence[int]) -> None:
        """
        Send data over the USB HID interface:

          - ``data`` is the data to send (a tuple/list of integers, or a
            bytearray).
        """
        ...
