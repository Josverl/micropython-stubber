""" """

from __future__ import annotations

from array import array
from typing import Callable, Tuple, overload

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

class RTC:
    """
    The RTC is an independent clock that keeps track of the date
    and time.

    Example usage::

        rtc = pyb.RTC()
        rtc.datetime((2014, 5, 1, 4, 13, 0, 0, 0))
        print(rtc.datetime())
    """

    def __init__(self) -> None:
        """
        Create an RTC object.
        """

    def datetime(self, datetimetuple: tuple[int, int, int, int, int, int, int, int], /) -> Tuple:
        """
        Get or set the date and time of the RTC.

        With no arguments, this method returns an 8-tuple with the current
        date and time.  With 1 argument (being an 8-tuple) it sets the date
        and time (and ``subseconds`` is reset to 255).

        The 8-tuple has the following format:

            (year, month, day, weekday, hours, minutes, seconds, subseconds)

        ``weekday`` is 1-7 for Monday through Sunday.

        ``subseconds`` counts down from 255 to 0
        """
        ...

    def wakeup(self, timeout: int, callback: Callable[[RTC], None] | None = None, /) -> None:
        """
        Set the RTC wakeup timer to trigger repeatedly at every ``timeout``
        milliseconds.  This trigger can wake the pyboard from both the sleep
        states: :meth:`pyb.stop` and :meth:`pyb.standby`.

        If ``timeout`` is ``None`` then the wakeup timer is disabled.

        If ``callback`` is given then it is executed at every trigger of the
        wakeup timer.  ``callback`` must take exactly one argument.
        """
        ...

    def info(self) -> int:
        """
        Get information about the startup time and reset source.

         - The lower 0xffff are the number of milliseconds the RTC took to
           start up.
         - Bit 0x10000 is set if a power-on reset occurred.
         - Bit 0x20000 is set if an external reset occurred
        """
        ...

    @overload
    def calibration(self) -> int:
        """
        Get or set RTC calibration.

        With no arguments, ``calibration()`` returns the current calibration
        value, which is an integer in the range [-511 : 512].  With one
        argument it sets the RTC calibration.

        The RTC Smooth Calibration mechanism adjusts the RTC clock rate by
        adding or subtracting the given number of ticks from the 32768 Hz
        clock over a 32 second period (corresponding to 2^20 clock ticks.)
        Each tick added will speed up the clock by 1 part in 2^20, or 0.954
        ppm; likewise the RTC clock it slowed by negative values. The
        usable calibration range is:
        (-511 * 0.954) ~= -487.5 ppm up to (512 * 0.954) ~= 488.5 ppm
        """

    @overload
    def calibration(self, cal: int, /) -> None:
        """
        Get or set RTC calibration.

        With no arguments, ``calibration()`` returns the current calibration
        value, which is an integer in the range [-511 : 512].  With one
        argument it sets the RTC calibration.

        The RTC Smooth Calibration mechanism adjusts the RTC clock rate by
        adding or subtracting the given number of ticks from the 32768 Hz
        clock over a 32 second period (corresponding to 2^20 clock ticks.)
        Each tick added will speed up the clock by 1 part in 2^20, or 0.954
        ppm; likewise the RTC clock it slowed by negative values. The
        usable calibration range is:
        (-511 * 0.954) ~= -487.5 ppm up to (512 * 0.954) ~= 488.5 ppm
        """
