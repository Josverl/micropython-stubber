""" """

from __future__ import annotations

from array import array
from typing import Any, overload

from _typeshed import Incomplete
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

class Servo:
    """
    Servo objects control standard hobby servo motors with 3-wires (ground, power,
    signal).  There are 4 positions on the pyboard where these motors can be plugged
    in: pins X1 through X4 are the signal pins, and next to them are 4 sets of power
    and ground pins.

    Example usage::

        import pyb

        s1 = pyb.Servo(1)   # create a servo object on position X1
        s2 = pyb.Servo(2)   # create a servo object on position X2

        s1.angle(45)        # move servo 1 to 45 degrees
        s2.angle(0)         # move servo 2 to 0 degrees

        # move servo1 and servo2 synchronously, taking 1500ms
        s1.angle(-60, 1500)
        s2.angle(30, 1500)

    .. note:: The Servo objects use Timer(5) to produce the PWM output.  You can
       use Timer(5) for Servo control, or your own purposes, but not both at the
       same time.
    """

    def __init__(self, id: int, /) -> None:
        """
        Create a servo object.  ``id`` is 1-4, and corresponds to pins X1 through X4.
        """

    @overload
    def angle(self) -> int:
        """
        If no arguments are given, this function returns the current angle.

        If arguments are given, this function sets the angle of the servo:

          - ``angle`` is the angle to move to in degrees.
          - ``time`` is the number of milliseconds to take to get to the specified
            angle.  If omitted, then the servo moves as quickly as possible to its
            new position.
        """

    @overload
    def angle(self, angle: int, time: int = 0, /) -> None:
        """
        If no arguments are given, this function returns the current angle.

        If arguments are given, this function sets the angle of the servo:

          - ``angle`` is the angle to move to in degrees.
          - ``time`` is the number of milliseconds to take to get to the specified
            angle.  If omitted, then the servo moves as quickly as possible to its
            new position.
        """

    @overload
    def speed(self) -> int:
        """
        If no arguments are given, this function returns the current speed.

        If arguments are given, this function sets the speed of the servo:

          - ``speed`` is the speed to change to, between -100 and 100.
          - ``time`` is the number of milliseconds to take to get to the specified
            speed.  If omitted, then the servo accelerates as quickly as possible.
        """

    @overload
    def speed(self, speed: int, time: int = 0, /) -> None:
        """
        If no arguments are given, this function returns the current speed.

        If arguments are given, this function sets the speed of the servo:

          - ``speed`` is the speed to change to, between -100 and 100.
          - ``time`` is the number of milliseconds to take to get to the specified
            speed.  If omitted, then the servo accelerates as quickly as possible.
        """

    @overload
    def speed(self) -> int:
        """
        If no arguments are given, this function returns the current speed.

        If arguments are given, this function sets the speed of the servo:

          - ``speed`` is the speed to change to, between -100 and 100.
          - ``time`` is the number of milliseconds to take to get to the specified
            speed.  If omitted, then the servo accelerates as quickly as possible.
        """

    @overload
    def speed(self, value: int, /) -> None:
        """
        If no arguments are given, this function returns the current speed.

        If arguments are given, this function sets the speed of the servo:

          - ``speed`` is the speed to change to, between -100 and 100.
          - ``time`` is the number of milliseconds to take to get to the specified
            speed.  If omitted, then the servo accelerates as quickly as possible.
        """

    def pulse_width(self, value: Any | None = None) -> Incomplete:
        """
        If no arguments are given, this function returns the current raw pulse-width
        value.

        If an argument is given, this function sets the raw pulse-width value.
        """
        ...

    @overload
    def calibration(self) -> tuple[int, int, int, int, int]:
        """
        If no arguments are given, this function returns the current calibration
        data, as a 5-tuple.

        If arguments are given, this function sets the timing calibration:

          - ``pulse_min`` is the minimum allowed pulse width.
          - ``pulse_max`` is the maximum allowed pulse width.
          - ``pulse_centre`` is the pulse width corresponding to the centre/zero position.
          - ``pulse_angle_90`` is the pulse width corresponding to 90 degrees.
          - ``pulse_speed_100`` is the pulse width corresponding to a speed of 100.
        """

    @overload
    def calibration(self, pulse_min: int, pulse_max: int, pulse_centre: int, /) -> None:
        """
        If no arguments are given, this function returns the current calibration
        data, as a 5-tuple.

        If arguments are given, this function sets the timing calibration:

          - ``pulse_min`` is the minimum allowed pulse width.
          - ``pulse_max`` is the maximum allowed pulse width.
          - ``pulse_centre`` is the pulse width corresponding to the centre/zero position.
          - ``pulse_angle_90`` is the pulse width corresponding to 90 degrees.
          - ``pulse_speed_100`` is the pulse width corresponding to a speed of 100.
        """

    @overload
    def calibration(
        self,
        pulse_min: int,
        pulse_max: int,
        pulse_centre: int,
        pulse_angle_90: int,
        pulse_speed_100: int,
        /,
    ) -> None:
        """
        If no arguments are given, this function returns the current calibration
        data, as a 5-tuple.

        If arguments are given, this function sets the timing calibration:

          - ``pulse_min`` is the minimum allowed pulse width.
          - ``pulse_max`` is the maximum allowed pulse width.
          - ``pulse_centre`` is the pulse width corresponding to the centre/zero position.
          - ``pulse_angle_90`` is the pulse width corresponding to 90 degrees.
          - ``pulse_speed_100`` is the pulse width corresponding to a speed of 100.
        """
