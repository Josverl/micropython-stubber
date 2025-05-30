""" """

from __future__ import annotations

from typing import Any, Callable, Tuple, overload

from _typeshed import Incomplete
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

class RTC:
    """
    The RTC is an independent clock that keeps track of the date
    and time.

    Example usage::

        rtc = machine.RTC()
        rtc.datetime((2020, 1, 21, 2, 10, 32, 36, 0))
        print(rtc.datetime())



    The documentation for RTC is in a poor state; better to experiment and use `dir`!
    """

    ALARM0: Incomplete
    """irq trigger source"""
    @overload
    def __init__(self, id: int = 0, /, *, datetime: tuple[int, int, int]):
        """
        Create an RTC object. See init for parameters of initialization.

        The documentation for RTC is in a poor state; better to experiment and use `dir`!
        """

    @overload
    def __init__(self, id: int = 0, /, *, datetime: tuple[int, int, int, int]):
        """
        Create an RTC object. See init for parameters of initialization.

        The documentation for RTC is in a poor state; better to experiment and use `dir`!
        """

    @overload
    def __init__(self, id: int = 0, /, *, datetime: tuple[int, int, int, int, int]):
        """
        Create an RTC object. See init for parameters of initialization.

        The documentation for RTC is in a poor state; better to experiment and use `dir`!
        """

    @overload
    def __init__(self, id: int = 0, /, *, datetime: tuple[int, int, int, int, int, int]):
        """
        Create an RTC object. See init for parameters of initialization.

        The documentation for RTC is in a poor state; better to experiment and use `dir`!
        """

    @overload
    def __init__(self, id: int = 0, /, *, datetime: tuple[int, int, int, int, int, int, int]):
        """
        Create an RTC object. See init for parameters of initialization.

        The documentation for RTC is in a poor state; better to experiment and use `dir`!
        """

    @overload
    def __init__(self, id: int = 0, /, *, datetime: tuple[int, int, int, int, int, int, int, int]):
        """
        Create an RTC object. See init for parameters of initialization.

        The documentation for RTC is in a poor state; better to experiment and use `dir`!
        """

    def datetime(self, datetimetuple: Any | None = None) -> Tuple:
        """
        Get or set the date and time of the RTC.

        With no arguments, this method returns an 8-tuple with the current
        date and time.  With 1 argument (being an 8-tuple) it sets the date
        and time.

        The 8-tuple has the following format:

            (year, month, day, weekday, hours, minutes, seconds, subseconds)

        The meaning of the ``subseconds`` field is hardware dependent.
        """
        ...

    @overload
    def init(self) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]])``
        """

    @overload
    def init(self, datetime: tuple[int, int, int], /) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]])``
        """

    @overload
    def init(self, datetime: tuple[int, int, int, int], /) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]])``
        """

    @overload
    def init(self, datetime: tuple[int, int, int, int, int], /) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]])``
        """

    @overload
    def init(self, datetime: tuple[int, int, int, int, int, int], /) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]])``
        """

    @overload
    def init(self, datetime: tuple[int, int, int, int, int, int, int], /) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]])``
        """

    @overload
    def init(self, datetime: tuple[int, int, int, int, int, int, int, int], /) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]])``
        """

    def now(self) -> Tuple:
        """
        Get get the current datetime tuple.
        """
        ...

    def deinit(self) -> None:
        """
        Resets the RTC to the time of January 1, 2015 and starts running it again.
        """
        ...

    @overload
    def alarm(self, id: int, time: int, /, *, repeat: bool = False) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

    @overload
    def alarm(self, id: int, time: tuple[int, int, int], /) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

    @overload
    def alarm(self, id: int, time: tuple[int, int, int, int], /) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

    @overload
    def alarm(self, id: int, time: tuple[int, int, int, int, int], /) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

    @overload
    def alarm(self, id: int, time: tuple[int, int, int, int, int, int], /) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

    @overload
    def alarm(self, id: int, time: tuple[int, int, int, int, int, int, int], /) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

    @overload
    def alarm(self, id: int, time: tuple[int, int, int, int, int, int, int, int], /) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

    def alarm_left(self, alarm_id: int = 0, /) -> int:
        """
        Get the number of milliseconds left before the alarm expires.
        """
        ...

    def cancel(self, alarm_id: int = 0, /) -> None:
        """
        Cancel a running alarm.
        """
        ...

    def irq(
        self,
        /,
        *,
        trigger: int,
        handler: Callable[[RTC], None] | None = None,
        wake: int = IDLE,
    ) -> None:
        """
        Create an irq object triggered by a real time clock alarm.

           - ``trigger`` must be ``RTC.ALARM0``
           - ``handler`` is the function to be called when the callback is triggered.
           - ``wake`` specifies the sleep mode from where this interrupt can wake
             up the system.
        """
        ...

    def memory(self, data: Any | None = None) -> bytes:
        """
        ``RTC.memory(data)`` will write *data* to the RTC memory, where *data* is any
        object which supports the buffer protocol (including `bytes`, `bytearray`,
        `memoryview` and `array.array`). ``RTC.memory()`` reads RTC memory and returns
        a `bytes` object.

        Data written to RTC user memory is persistent across restarts, including
        `machine.soft_reset()` and `machine.deepsleep()`.

        The maximum length of RTC user memory is 2048 bytes by default on esp32,
        and 492 bytes on esp8266.

        Availability: esp32, esp8266 ports.
        """
        ...
