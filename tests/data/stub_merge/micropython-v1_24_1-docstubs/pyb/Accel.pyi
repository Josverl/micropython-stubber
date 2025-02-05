""" """

from __future__ import annotations

from array import array
from typing import Tuple

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

class Accel:
    """
    Accel is an object that controls the accelerometer.  Example usage::

        accel = pyb.Accel()
        for i in range(10):
            print(accel.x(), accel.y(), accel.z())

    Raw values are between -32 and 31.
    """

    def __init__(self) -> None:
        """
        Create and return an accelerometer object.
        """

    def filtered_xyz(self) -> Tuple:
        """
        Get a 3-tuple of filtered x, y and z values.

        Implementation note: this method is currently implemented as taking the
        sum of 4 samples, sampled from the 3 previous calls to this function along
        with the sample from the current call.  Returned values are therefore 4
        times the size of what they would be from the raw x(), y() and z() calls.
        """
        ...

    def tilt(self) -> int:
        """
        Get the tilt register.
        """
        ...

    def x(self) -> int:
        """
        Get the x-axis value.
        """
        ...

    def y(self) -> int:
        """
        Get the y-axis value.
        """
        ...

    def z(self) -> int:
        """
        Get the z-axis value.
        """
        ...
