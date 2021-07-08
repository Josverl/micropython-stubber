# .. module:: utime
# origin: micropython\docs\library\utime.rst
# v1.16
"""
   :synopsis: time related functions

|see_cpython_module| :mod:`python:time`.

The ``utime`` module provides functions for getting the current time and date,
measuring time intervals, and for delays.

**Time Epoch**: Unix port uses standard for POSIX systems epoch of
1970-01-01 00:00:00 UTC. However, embedded ports use epoch of
2000-01-01 00:00:00 UTC.

**Maintaining actual calendar date/time**: This requires a
Real Time Clock (RTC). On systems with underlying OS (including some
RTOS), an RTC may be implicit. Setting and maintaining actual calendar
time is responsibility of OS/RTOS and is done outside of MicroPython,
it just uses OS API to query date/time. On baremetal ports however
system time depends on ``machine.RTC()`` object. The current calendar time
may be set using ``machine.RTC().datetime(tuple)`` function, and maintained
by following means:

* By a backup battery (which may be an additional, optional component for
  a particular board).
* Using networked time protocol (requires setup by a port/user).
* Set manually by a user on each power-up (many boards then maintain
  RTC time across hard resets, though some may require setting it again
  in such case).

If actual calendar time is not maintained with a system/MicroPython RTC,
functions below which require reference to current absolute time may
behave not as expected.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: utime
# .. function:: gmtime([secs])
def gmtime(secs: Optional[Any]) -> Any:
    """
               localtime([secs])

    Convert the time *secs* expressed in seconds since the Epoch (see above) into an
    8-tuple which contains: ``(year, month, mday, hour, minute, second, weekday, yearday)``
    If *secs* is not provided or None, then the current time from the RTC is used.

    The `gmtime()` function returns a date-time tuple in UTC, and `localtime()` returns a
    date-time tuple in local time.

    The format of the entries in the 8-tuple are:

    * year includes the century (for example 2014).
    * month   is 1-12
    * mday    is 1-31
    * hour    is 0-23
    * minute  is 0-59
    * second  is 0-59
    * weekday is 0-6 for Mon-Sun
    * yearday is 1-366
    """
    ...


# .. function:: sleep(seconds)
def sleep(seconds) -> Any:
    """
    Sleep for the given number of seconds. Some boards may accept *seconds* as a
    floating-point number to sleep for a fractional number of seconds. Note that
    other boards may not accept a floating-point argument, for compatibility with
    them use `sleep_ms()` and `sleep_us()` functions.
    """
    ...


# .. function:: sleep_us(us)
def sleep_us(us) -> Any:
    """
    Delay for given number of microseconds, should be positive or 0.
    """
    ...


# .. function:: ticks_us()
def ticks_us() -> Any:
    """
    Just like `ticks_ms()` above, but in microseconds.
    """
    ...


# .. function:: ticks_add(ticks, delta)
def ticks_add(ticks, delta) -> Any:
    """
    Offset ticks value by a given number, which can be either positive or negative.
    Given a *ticks* value, this function allows to calculate ticks value *delta*
    ticks before or after it, following modular-arithmetic definition of tick values
    (see `ticks_ms()` above). *ticks* parameter must be a direct result of call
    to `ticks_ms()`, `ticks_us()`, or `ticks_cpu()` functions (or from previous
    call to `ticks_add()`). However, *delta* can be an arbitrary integer number
    or numeric expression. `ticks_add()` is useful for calculating deadlines for
    events/tasks. (Note: you must use `ticks_diff()` function to work with
    deadlines.)

    Examples::

         # Find out what ticks value there was 100ms ago
         print(ticks_add(time.ticks_ms(), -100))

         # Calculate deadline for operation and test for it
         deadline = ticks_add(time.ticks_ms(), 200)
         while ticks_diff(deadline, time.ticks_ms()) > 0:
             do_a_little_of_something()

         # Find out TICKS_MAX used by this port
         print(ticks_add(0, -1))

    """
    ...


# .. function:: time()
class time:
    """
    Returns the number of seconds, as an integer, since the Epoch, assuming that
    underlying RTC is set and maintained as described above. If an RTC is not set, this
    function returns number of seconds since a port-specific reference point in time (for
    embedded boards without a battery-backed RTC, usually since power up or reset). If you
    want to develop portable MicroPython application, you should not rely on this function
    to provide higher than second precision.  If you need higher precision, absolute
    timestamps, use `time_ns()`.  If relative times are acceptable then use the
    `ticks_ms()` and `ticks_us()` functions.  If you need calendar time, `gmtime()` or
    `localtime()` without an argument is a better choice.

    .. admonition:: Difference to CPython
       :class: attention

       In CPython, this function returns number of
       seconds since Unix epoch, 1970-01-01 00:00 UTC, as a floating-point,
       usually having microsecond precision. With MicroPython, only Unix port
       uses the same Epoch, and if floating-point precision allows,
       returns sub-second precision. Embedded hardware usually doesn't have
       floating-point precision to represent both long time ranges and subsecond
       precision, so they use integer value with second precision. Some embedded
       hardware also lacks battery-powered RTC, so returns number of seconds
       since last power-up or from other relative, hardware-specific point
       (e.g. reset).
    """

    def __init__(
        self,
    ) -> None:
        ...
