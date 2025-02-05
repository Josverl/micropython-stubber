""" """

from __future__ import annotations

from array import array
from typing import overload

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

class LED:
    """
    The LED object controls an individual LED (Light Emitting Diode).
    """

    def __init__(self, id: int, /) -> None:
        """
        Create an LED object associated with the given LED:

          - ``id`` is the LED number, 1-4.
        """

    @overload
    def intensity(self) -> int:
        """
        Get or set the LED intensity.  Intensity ranges between 0 (off) and 255 (full on).
        If no argument is given, return the LED intensity.
        If an argument is given, set the LED intensity and return ``None``.

        *Note:* Only LED(3) and LED(4) can have a smoothly varying intensity, and
        they use timer PWM to implement it.  LED(3) uses Timer(2) and LED(4) uses
        Timer(3).  These timers are only configured for PWM if the intensity of the
        relevant LED is set to a value between 1 and 254.  Otherwise the timers are
        free for general purpose use.
        """

    @overload
    def intensity(self, value: int, /) -> None:
        """
        Get or set the LED intensity.  Intensity ranges between 0 (off) and 255 (full on).
        If no argument is given, return the LED intensity.
        If an argument is given, set the LED intensity and return ``None``.

        *Note:* Only LED(3) and LED(4) can have a smoothly varying intensity, and
        they use timer PWM to implement it.  LED(3) uses Timer(2) and LED(4) uses
        Timer(3).  These timers are only configured for PWM if the intensity of the
        relevant LED is set to a value between 1 and 254.  Otherwise the timers are
        free for general purpose use.
        """

    def off(self) -> None:
        """
        Turn the LED off.
        """
        ...

    def on(self) -> None:
        """
        Turn the LED on, to maximum intensity.
        """
        ...

    def toggle(self) -> None:
        """
        Toggle the LED between on (maximum intensity) and off.  If the LED is at
        non-zero intensity then it is considered "on" and toggle will turn it off.
        """
        ...
