""" """

from __future__ import annotations

from typing import overload

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

class PWM:
    """
    This class provides pulse width modulation output.

    Example usage::

        from machine import PWM

        pwm = PWM(pin)          # create a PWM object on a pin
        pwm.duty_u16(32768)     # set duty to 50%

        # reinitialise with a period of 200us, duty of 5us
        pwm.init(freq=5000, duty_ns=5000)

        pwm.duty_ns(3000)       # set pulse width to 3us

        pwm.deinit()


    Limitations of PWM
    ------------------

    * Not all frequencies can be generated with absolute accuracy due to
      the discrete nature of the computing hardware.  Typically the PWM frequency
      is obtained by dividing some integer base frequency by an integer divider.
      For example, if the base frequency is 80MHz and the required PWM frequency is
      300kHz the divider must be a non-integer number 80000000 / 300000 = 266.67.
      After rounding the divider is set to 267 and the PWM frequency will be
      80000000 / 267 = 299625.5 Hz, not 300kHz.  If the divider is set to 266 then
      the PWM frequency will be 80000000 / 266 = 300751.9 Hz, but again not 300kHz.

    * The duty cycle has the same discrete nature and its absolute accuracy is not
      achievable.  On most hardware platforms the duty will be applied at the next
      frequency period.  Therefore, you should wait more than "1/frequency" before
      measuring the duty.

    * The frequency and the duty cycle resolution are usually interdependent.
      The higher the PWM frequency the lower the duty resolution which is available,
      and vice versa. For example, a 300kHz PWM frequency can have a duty cycle
      resolution of 8 bit, not 16-bit as may be expected.  In this case, the lowest
      8 bits of *duty_u16* are insignificant. So::

        pwm=PWM(Pin(13), freq=300_000, duty_u16=2**16//2)

      and::

        pwm=PWM(Pin(13), freq=300_000, duty_u16=2**16//2 + 255)

      will generate PWM with the same 50% duty cycle.
    """

    def __init__(
        self,
        dest: Pin | int,
        /,
        *,
        freq: int = ...,
        duty_u16: int = ...,
        duty_ns: int = ...,
    ) -> None:
        """
        Construct and return a new PWM object using the following parameters:

           - *dest* is the entity on which the PWM is output, which is usually a
             :ref:`machine.Pin <machine.Pin>` object, but a port may allow other values,
             like integers.
           - *freq* should be an integer which sets the frequency in Hz for the
             PWM cycle.
           - *duty_u16* sets the duty cycle as a ratio ``duty_u16 / 65535``.
           - *duty_ns* sets the pulse width in nanoseconds.

        Setting *freq* may affect other PWM objects if the objects share the same
        underlying PWM generator (this is hardware specific).
        Only one of *duty_u16* and *duty_ns* should be specified at a time.
        """

    def init(self, *, freq: int = ..., duty_u16: int = ..., duty_ns: int = ...) -> None:
        """
        Modify settings for the PWM object.  See the above constructor for details
        about the parameters.
        """
        ...

    def deinit(self) -> None:
        """
        Disable the PWM output.
        """
        ...

    @overload
    def freq(self) -> int:
        """
        Get or set the current frequency of the PWM output.

        With no arguments the frequency in Hz is returned.

        With a single *value* argument the frequency is set to that value in Hz.  The
        method may raise a ``ValueError`` if the frequency is outside the valid range.
        """

    @overload
    def freq(
        self,
        value: int,
        /,
    ) -> None:
        """
        Get or set the current frequency of the PWM output.

        With no arguments the frequency in Hz is returned.

        With a single *value* argument the frequency is set to that value in Hz.  The
        method may raise a ``ValueError`` if the frequency is outside the valid range.
        """

    @overload
    def duty_u16(self) -> int:
        """
        Get or set the current duty cycle of the PWM output, as an unsigned 16-bit
        value in the range 0 to 65535 inclusive.

        With no arguments the duty cycle is returned.

        With a single *value* argument the duty cycle is set to that value, measured
        as the ratio ``value / 65535``.
        """

    @overload
    def duty_u16(
        self,
        value: int,
        /,
    ) -> None:
        """
        Get or set the current duty cycle of the PWM output, as an unsigned 16-bit
        value in the range 0 to 65535 inclusive.

        With no arguments the duty cycle is returned.

        With a single *value* argument the duty cycle is set to that value, measured
        as the ratio ``value / 65535``.
        """

    @overload
    def duty_ns(self) -> int:
        """
        Get or set the current pulse width of the PWM output, as a value in nanoseconds.

        With no arguments the pulse width in nanoseconds is returned.

        With a single *value* argument the pulse width is set to that value.
        """

    @overload
    def duty_ns(
        self,
        value: int,
        /,
    ) -> None:
        """
        Get or set the current pulse width of the PWM output, as a value in nanoseconds.

        With no arguments the pulse width in nanoseconds is returned.

        With a single *value* argument the pulse width is set to that value.
        """
