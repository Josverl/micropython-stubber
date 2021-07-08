# .. module:: machine
# origin: micropython\docs\library\machine.rst
# v1.16
"""
   :synopsis: functions related to the hardware

The ``machine`` module contains specific functions related to the hardware
on a particular board. Most functions in this module allow to achieve direct
and unrestricted access to and control of hardware blocks on a system
(like CPU, timers, buses, etc.). Used incorrectly, this can lead to
malfunction, lockups, crashes of your board, and in extreme cases, hardware
damage.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: machine
# .. function:: reset()
def reset() -> Any:
    """
    Resets the device in a manner similar to pushing the external RESET
    button.
    """
    ...


# .. function:: reset_cause()
def reset_cause() -> Any:
    """
    Get the reset cause. See :ref:`constants <machine_constants>` for the possible return values.
    """
    ...


# .. function:: disable_irq()
def disable_irq() -> Any:
    """
    Disable interrupt requests.
    Returns the previous IRQ state which should be considered an opaque value.
    This return value should be passed to the `enable_irq()` function to restore
    interrupts to their original state, before `disable_irq()` was called.
    """
    ...


# .. function:: freq([hz])
def freq(hz: Optional[Any]) -> Any:
    """
    Returns the CPU frequency in hertz.

    On some ports this can also be used to set the CPU frequency by passing in *hz*.
    """
    ...


# .. function:: sleep()
def sleep() -> Any:
    """
    .. note:: This function is deprecated, use `lightsleep()` instead with no arguments.
    """
    ...


# .. function:: deepsleep([time_ms])
def deepsleep(time_ms: Optional[Any]) -> Any:
    """
    Stops execution in an attempt to enter a low power state.

    If *time_ms* is specified then this will be the maximum time in milliseconds that
    the sleep will last for.  Otherwise the sleep can last indefinitely.

    With or without a timeout, execution may resume at any time if there are events
    that require processing.  Such events, or wake sources, should be configured before
    sleeping, like `Pin` change or `RTC` timeout.

    The precise behaviour and power-saving capabilities of lightsleep and deepsleep is
    highly dependent on the underlying hardware, but the general properties are:

    * A deepsleep may not retain RAM or any other state of the system (for example
      peripherals or network interfaces).  Upon wake execution is resumed from the main
      script, similar to a hard or power-on reset. The `reset_cause()` function will
      return `machine.DEEPSLEEP` and this can be used to distinguish a deepsleep wake
      from other resets.
    """
    ...


# .. function:: unique_id()
def unique_id() -> Any:
    """
    Returns a byte string with a unique identifier of a board/SoC. It will vary
    from a board/SoC instance to another, if underlying hardware allows. Length
    varies by hardware (so use substring of a full value if you expect a short
    ID). In some MicroPython ports, ID corresponds to the network MAC address.
    """
    ...


# .. function:: rng()
def rng() -> Any:
    """
    Return a 24-bit software generated random number.

    Availability: WiPy.
    """
    ...


# .. data:: machine.IDLE
# .. data:: machine.PWRON_RESET
# .. data:: machine.WLAN_WAKE
# .. toctree::
# .. currentmodule:: machine
# currentmodule:: machine
# .. _machine.Pin:
# .. class:: Pin(id, mode=-1, pull=-1, *, value, drive, alt)
# .. class:: Pin(id, mode=-1, pull=-1, *, value, drive, alt)

# class:: Pin
class Pin:
    """
    Access the pin peripheral (GPIO pin) associated with the given ``id``.  If
    additional arguments are given in the constructor then they are used to initialise
    the pin.  Any settings that are not specified will remain in their previous state.

    The arguments are:

      - ``id`` is mandatory and can be an arbitrary object.  Among possible value
        types are: int (an internal Pin identifier), str (a Pin name), and tuple
        (pair of [port, pin]).

      - ``mode`` specifies the pin mode, which can be one of:

        - ``Pin.IN`` - Pin is configured for input.  If viewed as an output the pin
          is in high-impedance state.

        - ``Pin.OUT`` - Pin is configured for (normal) output.

        - ``Pin.OPEN_DRAIN`` - Pin is configured for open-drain output. Open-drain
          output works in the following way: if the output value is set to 0 the pin
          is active at a low level; if the output value is 1 the pin is in a high-impedance
          state.  Not all ports implement this mode, or some might only on certain pins.

        - ``Pin.ALT`` - Pin is configured to perform an alternative function, which is
          port specific.  For a pin configured in such a way any other Pin methods
          (except :meth:`Pin.init`) are not applicable (calling them will lead to undefined,
          or a hardware-specific, result).  Not all ports implement this mode.

        - ``Pin.ALT_OPEN_DRAIN`` - The Same as ``Pin.ALT``, but the pin is configured as
          open-drain.  Not all ports implement this mode.

      - ``pull`` specifies if the pin has a (weak) pull resistor attached, and can be
        one of:

        - ``None`` - No pull up or down resistor.
        - ``Pin.PULL_UP`` - Pull up resistor enabled.
        - ``Pin.PULL_DOWN`` - Pull down resistor enabled.

      - ``value`` is valid only for Pin.OUT and Pin.OPEN_DRAIN modes and specifies initial
        output pin value if given, otherwise the state of the pin peripheral remains
        unchanged.

      - ``drive`` specifies the output power of the pin and can be one of: ``Pin.LOW_POWER``,
        ``Pin.MED_POWER`` or ``Pin.HIGH_POWER``.  The actual current driving capabilities
        are port dependent.  Not all ports implement this argument.

      - ``alt`` specifies an alternate function for the pin and the values it can take are
        port dependent.  This argument is valid only for ``Pin.ALT`` and ``Pin.ALT_OPEN_DRAIN``
        modes.  It may be used when a pin supports more than one alternate function.  If only
        one pin alternate function is supported the this argument is not required.  Not all
        ports implement this argument.

    As specified above, the Pin class allows to set an alternate function for a particular
    pin, but it does not specify any further operations on such a pin.  Pins configured in
    alternate-function mode are usually not used as GPIO but are instead driven by other
    hardware peripherals.  The only operation supported on such a pin is re-initialising,
    by calling the constructor or :meth:`Pin.init` method.  If a pin that is configured in
    alternate-function mode is re-initialised with ``Pin.IN``, ``Pin.OUT``, or
    ``Pin.OPEN_DRAIN``, the alternate function will be removed from the pin.
    """

    def __init__(self, id, mode=-1, pull=-1, *, value, drive, alt) -> None:
        ...

    # .. method:: Pin.init(mode=-1, pull=-1, *, value, drive, alt)
    def init(self, mode=-1, pull=-1, *, value, drive, alt) -> Any:
        """
        Re-initialise the pin using the given parameters.  Only those arguments that
        are specified will be set.  The rest of the pin peripheral state will remain
        unchanged.  See the constructor documentation for details of the arguments.

        Returns ``None``.
        """
        ...

    # .. method:: Pin.__call__([x])
    def __call__(self, x: Optional[Any]) -> Any:
        """
        Pin objects are callable.  The call method provides a (fast) shortcut to set
        and get the value of the pin.  It is equivalent to Pin.value([x]).
        See :meth:`Pin.value` for more details.
        """
        ...

    # .. method:: Pin.off()
    def off(
        self,
    ) -> Any:
        """
        Set pin to "0" output level.
        """
        ...

    # .. method:: Pin.low()
    def low(
        self,
    ) -> Any:
        """
        Set pin to "0" output level.

        Availability: nrf, rp2, stm32 ports.
        """
        ...

    # .. method:: Pin.mode([mode])
    def mode(self, mode: Optional[Any]) -> Any:
        """
        Get or set the pin mode.
        See the constructor documentation for details of the ``mode`` argument.

        Availability: cc3200, stm32 ports.
        """
        ...

    # .. method:: Pin.drive([drive])
    def drive(self, drive: Optional[Any]) -> Any:
        """
        Get or set the pin drive strength.
        See the constructor documentation for details of the ``drive`` argument.

        Availability: cc3200 port.
        """
        ...


# .. data:: Pin.IN
# .. data:: Pin.PULL_UP
# .. data:: Pin.LOW_POWER
# .. data:: Pin.IRQ_FALLING
# .. currentmodule:: machine
# currentmodule:: machine
# .. _machine.Signal:
# .. class:: Signal(pin_obj, invert=False)
# .. class:: Signal(pin_obj, invert=False)

# class:: Signal
class Signal:
    """
            Signal(pin_arguments..., *, invert=False)

    Create a Signal object. There're two ways to create it:

    * By wrapping existing Pin object - universal method which works for
      any board.
    * By passing required Pin parameters directly to Signal constructor,
      skipping the need to create intermediate Pin object. Available on
      many, but not all boards.

    The arguments are:

      - ``pin_obj`` is existing Pin object.

      - ``pin_arguments`` are the same arguments as can be passed to Pin constructor.

      - ``invert`` - if True, the signal will be inverted (active low).
    """

    def __init__(self, pin_obj, invert=False) -> None:
        ...

    # .. method:: Signal.value([x])
    def value(self, x: Optional[Any]) -> Any:
        """
        This method allows to set and get the value of the signal, depending on whether
        the argument ``x`` is supplied or not.

        If the argument is omitted then this method gets the signal level, 1 meaning
        signal is asserted (active) and 0 - signal inactive.

        If the argument is supplied then this method sets the signal level. The
        argument ``x`` can be anything that converts to a boolean. If it converts
        to ``True``, the signal is active, otherwise it is inactive.

        Correspondence between signal being active and actual logic level on the
        underlying pin depends on whether signal is inverted (active-low) or not.
        For non-inverted signal, active status corresponds to logical 1, inactive -
        to logical 0. For inverted/active-low signal, active status corresponds
        to logical 0, while inactive - to logical 1.
        """
        ...

    # .. method:: Signal.off()
    def off(
        self,
    ) -> Any:
        """
        Deactivate signal.
        """
        ...


# .. currentmodule:: machine
# currentmodule:: machine
# .. _machine.ADC:
# .. class:: ADC(id)
# .. class:: ADC(id)

# class:: ADC
class ADC:
    """
    Access the ADC associated with a source identified by *id*.  This
    *id* may be an integer (usually specifying a channel number), a
    :ref:`Pin <machine.Pin>` object, or other value supported by the
    underlying machine.
    """

    def __init__(self, id) -> None:
        ...

    # .. method:: ADC.read_u16()
    def read_u16(
        self,
    ) -> Any:
        """
        Take an analog reading and return an integer in the range 0-65535.
        The return value represents the raw reading taken by the ADC, scaled
        such that the minimum value is 0 and the maximum value is 65535.
        """
        ...


# .. currentmodule:: machine
# currentmodule:: machine
# .. _machine.PWM:
# .. class:: PWM(dest, \*, freq, duty_u16, duty_ns)
# .. class:: PWM(dest, \*, freq, duty_u16, duty_ns)

# class:: PWM
class PWM:
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

    def __init__(self, dest, *, freq, duty_u16, duty_ns) -> None:
        ...

    # .. method:: PWM.init(\*, freq, duty_u16, duty_ns)
    def init(self, *, freq, duty_u16, duty_ns) -> Any:
        """
        Modify settings for the PWM object.  See the above constructor for details
        about the parameters.
        """
        ...

    # .. method:: PWM.freq([value])
    def freq(self, value: Optional[Any]) -> Any:
        """
        Get or set the current frequency of the PWM output.

        With no arguments the frequency in Hz is returned.

        With a single *value* argument the frequency is set to that value in Hz.  The
        method may raise a ``ValueError`` if the frequency is outside the valid range.
        """
        ...

    # .. method:: PWM.duty_ns([value])
    def duty_ns(self, value: Optional[Any]) -> Any:
        """
        Get or set the current pulse width of the PWM output, as a value in nanoseconds.

        With no arguments the pulse width in nanoseconds is returned.

        With a single *value* argument the pulse width is set to that value.
        """
        ...


# .. currentmodule:: machine
# currentmodule:: machine
# .. _machine.UART:
# .. class:: UART(id, ...)
# .. class:: UART(id, ...)

# class:: UART
class UART:
    """
    Construct a UART object of the given id.
    """

    def __init__(self, id, *args) -> None:
        ...

    # .. method:: UART.init(baudrate=9600, bits=8, parity=None, stop=1, *, ...)
    def init(self, baudrate=9600, bits=8, parity=None, stop=1, *args) -> Any:
        """
        Initialise the UART bus with the given parameters:

          - *baudrate* is the clock rate.
          - *bits* is the number of bits per character, 7, 8 or 9.
          - *parity* is the parity, ``None``, 0 (even) or 1 (odd).
          - *stop* is the number of stop bits, 1 or 2.

        Additional keyword-only parameters that may be supported by a port are:

          - *tx* specifies the TX pin to use.
          - *rx* specifies the RX pin to use.
          - *txbuf* specifies the length in characters of the TX buffer.
          - *rxbuf* specifies the length in characters of the RX buffer.
          - *timeout* specifies the time to wait for the first character (in ms).
          - *timeout_char* specifies the time to wait between characters (in ms).
          - *invert* specifies which lines to invert.

        On the WiPy only the following keyword-only parameter is supported:

          - *pins* is a 4 or 2 item list indicating the TX, RX, RTS and CTS pins (in that order).
            Any of the pins can be None if one wants the UART to operate with limited functionality.
            If the RTS pin is given the the RX pin must be given as well. The same applies to CTS.
            When no pins are given, then the default set of TX and RX pins is taken, and hardware
            flow control will be disabled. If *pins* is ``None``, no pin assignment will be made.
        """
        ...

    # .. method:: UART.any()
    def any(
        self,
    ) -> Any:
        """
        Returns an integer counting the number of characters that can be read without
        blocking.  It will return 0 if there are no characters available and a positive
        number if there are characters.  The method may return 1 even if there is more
        than one character available for reading.

        For more sophisticated querying of available characters use select.poll::

         poll = select.poll()
         poll.register(uart, select.POLLIN)
         poll.poll(timeout)
        """
        ...

    # .. method:: UART.readinto(buf[, nbytes])
    def readinto(self, buf, nbytes: Optional[Any]) -> Any:
        """
        Read bytes into the ``buf``.  If ``nbytes`` is specified then read at most
        that many bytes.  Otherwise, read at most ``len(buf)`` bytes. It may return sooner if a timeout
        is reached. The timeout is configurable in the constructor.

        Return value: number of bytes read and stored into ``buf`` or ``None`` on
        timeout.
        """
        ...

    # .. method:: UART.write(buf)
    def write(self, buf) -> Any:
        """
        Write the buffer of bytes to the bus.

        Return value: number of bytes written or ``None`` on timeout.
        """
        ...

    # .. method:: UART.irq(trigger, priority=1, handler=None, wake=machine.IDLE)
    def irq(self, trigger, priority=1, handler=None, wake=IDLE) -> Any:
        """
        Create a callback to be triggered when data is received on the UART.

            - *trigger* can only be ``UART.RX_ANY``
            - *priority* level of the interrupt. Can take values in the range 1-7.
              Higher values represent higher priorities.
            - *handler* an optional function to be called when new characters arrive.
            - *wake* can only be ``machine.IDLE``.

        .. note::

           The handler will be called whenever any of the following two conditions are met:

               - 8 new characters have been received.
               - At least 1 new character is waiting in the Rx buffer and the Rx line has been
                 silent for the duration of 1 complete frame.

           This means that when the handler function is called there will be between 1 to 8
           characters waiting.

        Returns an irq object.

        Availability: WiPy.
        """
        ...


# .. data:: UART.RX_ANY
# .. currentmodule:: machine
# currentmodule:: machine
# .. _machine.SPI:
# .. class:: SPI(id, ...)
# .. class:: SPI(id, ...)

# class:: SPI
class SPI:
    """
    Construct an SPI object on the given bus, *id*. Values of *id* depend
    on a particular port and its hardware. Values 0, 1, etc. are commonly used
    to select hardware SPI block #0, #1, etc.

    With no additional parameters, the SPI object is created but not
    initialised (it has the settings from the last initialisation of
    the bus, if any).  If extra arguments are given, the bus is initialised.
    See ``init`` for parameters of initialisation.
    """

    def __init__(self, id, *args) -> None:
        ...

    # .. method:: SPI.init(baudrate=1000000, *, polarity=0, phase=0, bits=8, firstbit=SPI.MSB, sck=None, mosi=None, miso=None, pins=(SCK, MOSI, MISO))
    def init(
        self,
        baudrate=1000000,
        *,
        polarity=0,
        phase=0,
        bits=8,
        firstbit=MSB,
        sck=None,
        mosi=None,
        miso=None,
        pins=(SCK, MOSI, MISO),
    ) -> Any:
        """
        Initialise the SPI bus with the given parameters:

          - ``baudrate`` is the SCK clock rate.
          - ``polarity`` can be 0 or 1, and is the level the idle clock line sits at.
          - ``phase`` can be 0 or 1 to sample data on the first or second clock edge
            respectively.
          - ``bits`` is the width in bits of each transfer. Only 8 is guaranteed to be supported by all hardware.
          - ``firstbit`` can be ``SPI.MSB`` or ``SPI.LSB``.
          - ``sck``, ``mosi``, ``miso`` are pins (machine.Pin) objects to use for bus signals. For most
            hardware SPI blocks (as selected by ``id`` parameter to the constructor), pins are fixed
            and cannot be changed. In some cases, hardware blocks allow 2-3 alternative pin sets for
            a hardware SPI block. Arbitrary pin assignments are possible only for a bitbanging SPI driver
            (``id`` = -1).
          - ``pins`` - WiPy port doesn't ``sck``, ``mosi``, ``miso`` arguments, and instead allows to
            specify them as a tuple of ``pins`` parameter.

        In the case of hardware SPI the actual clock frequency may be lower than the
        requested baudrate. This is dependant on the platform hardware. The actual
        rate may be determined by printing the SPI object.
        """
        ...

    # .. method:: SPI.read(nbytes, write=0x00)
    def read(self, nbytes, write=0x00) -> Any:
        """
        Read a number of bytes specified by ``nbytes`` while continuously writing
        the single byte given by ``write``.
        Returns a ``bytes`` object with the data that was read.
        """
        ...

    # .. method:: SPI.write(buf)
    def write(self, buf) -> Any:
        """
        Write the bytes contained in ``buf``.
        Returns ``None``.

        Note: on WiPy this function returns the number of bytes written.
        """
        ...


# .. data:: SPI.MASTER
# .. data:: SPI.MSB
# .. data:: SPI.LSB
# .. currentmodule:: machine
# currentmodule:: machine
# .. _machine.I2C:
# .. class:: I2C(id, *, scl, sda, freq=400000)
# .. class:: I2C(id, *, scl, sda, freq=400000)

# class:: I2C
class I2C:
    """
    Construct and return a new I2C object using the following parameters:

       - *id* identifies a particular I2C peripheral.  Allowed values for
         depend on the particular port/board
       - *scl* should be a pin object specifying the pin to use for SCL.
       - *sda* should be a pin object specifying the pin to use for SDA.
       - *freq* should be an integer which sets the maximum frequency
         for SCL.

    Note that some ports/boards will have default values of *scl* and *sda*
    that can be changed in this constructor.  Others will have fixed values
    of *scl* and *sda* that cannot be changed.
    """

    def __init__(self, id, *, scl, sda, freq=400000) -> None:
        ...

    # .. method:: I2C.init(scl, sda, *, freq=400000)
    def init(self, scl, sda, *, freq=400000) -> Any:
        """
        Initialise the I2C bus with the given arguments:

           - *scl* is a pin object for the SCL line
           - *sda* is a pin object for the SDA line
           - *freq* is the SCL clock rate
        """
        ...

    # .. method:: I2C.scan()
    def scan(
        self,
    ) -> Any:
        """
        Scan all I2C addresses between 0x08 and 0x77 inclusive and return a list of
        those that respond.  A device responds if it pulls the SDA line low after
        its address (including a write bit) is sent on the bus.
        """
        ...

    # .. method:: I2C.start()
    def start(
        self,
    ) -> Any:
        """
        Generate a START condition on the bus (SDA transitions to low while SCL is high).
        """
        ...

    # .. method:: I2C.readinto(buf, nack=True, /)
    def readinto(self, buf, nack=True, /) -> Any:
        """
        Reads bytes from the bus and stores them into *buf*.  The number of bytes
        read is the length of *buf*.  An ACK will be sent on the bus after
        receiving all but the last byte.  After the last byte is received, if *nack*
        is true then a NACK will be sent, otherwise an ACK will be sent (and in this
        case the slave assumes more bytes are going to be read in a later call).
        """
        ...

    # .. method:: I2C.readfrom(addr, nbytes, stop=True, /)
    def readfrom(self, addr, nbytes, stop=True, /) -> Any:
        """
        Read *nbytes* from the slave specified by *addr*.
        If *stop* is true then a STOP condition is generated at the end of the transfer.
        Returns a `bytes` object with the data read.
        """
        ...

    # .. method:: I2C.writeto(addr, buf, stop=True, /)
    def writeto(self, addr, buf, stop=True, /) -> Any:
        """
        Write the bytes from *buf* to the slave specified by *addr*.  If a
        NACK is received following the write of a byte from *buf* then the
        remaining bytes are not sent.  If *stop* is true then a STOP condition is
        generated at the end of the transfer, even if a NACK is received.
        The function returns the number of ACKs that were received.
        """
        ...

    # .. method:: I2C.readfrom_mem(addr, memaddr, nbytes, *, addrsize=8)
    def readfrom_mem(self, addr, memaddr, nbytes, *, addrsize=8) -> Any:
        """
        Read *nbytes* from the slave specified by *addr* starting from the memory
        address specified by *memaddr*.
        The argument *addrsize* specifies the address size in bits.
        Returns a `bytes` object with the data read.
        """
        ...

    # .. method:: I2C.writeto_mem(addr, memaddr, buf, *, addrsize=8)
    def writeto_mem(self, addr, memaddr, buf, *, addrsize=8) -> Any:
        """
        Write *buf* to the slave specified by *addr* starting from the
        memory address specified by *memaddr*.
        The argument *addrsize* specifies the address size in bits (on ESP8266
        this argument is not recognised and the address size is always 8 bits).

        The method returns ``None``.
        """
        ...


# .. currentmodule:: machine
# currentmodule:: machine
# .. _machine.RTC:
# .. class:: RTC(id=0, ...)
# .. class:: RTC(id=0, ...)

# class:: RTC
class RTC:
    """
    Create an RTC object. See init for parameters of initialization.
    """

    def __init__(self, id=0, *args) -> None:
        ...

    # .. method:: RTC.datetime([datetimetuple])
    def datetime(self, datetimetuple: Optional[Any]) -> Any:
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

    # .. method:: RTC.now()
    def now(
        self,
    ) -> Any:
        """
        Get get the current datetime tuple.
        """
        ...

    # .. method:: RTC.alarm(id, time, *, repeat=False)
    def alarm(self, id, time, *, repeat=False) -> Any:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """
        ...

    # .. method:: RTC.cancel(alarm_id=0)
    def cancel(self, alarm_id=0) -> Any:
        """
        Cancel a running alarm.
        """
        ...


# .. data:: RTC.ALARM0
# .. currentmodule:: machine
# currentmodule:: machine
# .. _machine.Timer:
# .. note::
# .. class:: Timer(id, ...)
# .. class:: Timer(id, ...)

# class:: Timer
class Timer:
    """
    Construct a new timer object of the given id. Id of -1 constructs a
    virtual timer (if supported by a board).

    See ``init`` for parameters of initialisation.
    """

    def __init__(self, id, *args) -> None:
        ...

    # .. method:: Timer.init(*, mode=Timer.PERIODIC, period=-1, callback=None)
    def init(self, *, mode=PERIODIC, period=-1, callback=None) -> Any:
        """
        Initialise the timer. Example::

            tim.init(period=100)                         # periodic with 100ms period
            tim.init(mode=Timer.ONE_SHOT, period=1000)   # one shot firing after 1000ms

        Keyword arguments:

          - ``mode`` can be one of:

            - ``Timer.ONE_SHOT`` - The timer runs once until the configured
              period of the channel expires.
            - ``Timer.PERIODIC`` - The timer runs periodically at the configured
              frequency of the channel.
        """
        ...


# .. data:: Timer.ONE_SHOT
# .. currentmodule:: machine
# currentmodule:: machine
# .. _machine.WDT:
# .. class:: WDT(id=0, timeout=5000)
# .. class:: WDT(id=0, timeout=5000)

# class:: WDT
class WDT:
    """
    Create a WDT object and start it. The timeout must be given in milliseconds.
    Once it is running the timeout cannot be changed and the WDT cannot be stopped either.

    Notes: On the esp32 the minimum timeout is 1 second. On the esp8266 a timeout
    cannot be specified, it is determined by the underlying system.
    """

    def __init__(self, id=0, timeout=5000) -> None:
        ...

    # .. method:: wdt.feed()
    def feed(
        self,
    ) -> Any:
        """
        Feed the WDT to prevent it from resetting the system. The application
        should place this call in a sensible place ensuring that the WDT is
        only fed after verifying that everything is functioning correctly.
        """
        ...


# .. currentmodule:: machine
# currentmodule:: machine
# .. _machine.SD:
# .. warning::
# .. class:: SD(id,... )
# .. class:: SD(id,... )

# class:: SD
class SD:
    """
    Create a SD card object. See ``init()`` for parameters if initialization.
    """

    def __init__(self, id, *args) -> None:
        ...

    # .. method:: SD.init(id=0, pins=('GP10', 'GP11', 'GP15'))
    def init(self, id=0, pins=("GP10", "GP11", "GP15")) -> Any:
        """
        Enable the SD card. In order to initialize the card, give it a 3-tuple:
        ``(clk_pin, cmd_pin, dat0_pin)``.
        """
        ...


# .. currentmodule:: machine
# currentmodule:: machine
# .. _machine.SDCard:
# .. class:: SDCard(slot=1, width=1, cd=None, wp=None, sck=None, miso=None, mosi=None, cs=None, freq=20000000)
# .. class:: SDCard(slot=1, width=1, cd=None, wp=None, sck=None, miso=None, mosi=None, cs=None, freq=20000000)

# class:: SDCard
class SDCard:
    """
    This class provides access to SD or MMC storage cards using either
    a dedicated SD/MMC interface hardware or through an SPI channel.
    The class implements the block protocol defined by :class:`uos.AbstractBlockDev`.
    This allows the mounting of an SD card to be as simple as::

      uos.mount(machine.SDCard(), "/sd")

    The constructor takes the following parameters:

     - *slot* selects which of the available interfaces to use. Leaving this
       unset will select the default interface.

     - *width* selects the bus width for the SD/MMC interface.

     - *cd* can be used to specify a card-detect pin.

     - *wp* can be used to specify a write-protect pin.

     - *sck* can be used to specify an SPI clock pin.

     - *miso* can be used to specify an SPI miso pin.

     - *mosi* can be used to specify an SPI mosi pin.

     - *cs* can be used to specify an SPI chip select pin.

     - *freq* selects the SD/MMC interface frequency in Hz (only supported on the ESP32).
    """

    def __init__(
        self,
        slot=1,
        width=1,
        cd=None,
        wp=None,
        sck=None,
        miso=None,
        mosi=None,
        cs=None,
        freq=20000000,
    ) -> None:
        ...
