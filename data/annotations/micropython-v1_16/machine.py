"""Module: 'machine' on micropython-1.16

The ``machine`` module contains specific functions related to the hardware
on a particular board. Most functions in this module allow to achieve direct
and unrestricted access to and control of hardware blocks on a system
(like CPU, timers, buses, etc.). Used incorrectly, this can lead to
malfunction, lockups, crashes of your board, and in extreme cases, hardware
damage.

https://docs.micropython.org/en/latest/library/machine.html
"""
# MCU: {'ver': '1.16', 'port': 'esp32', 'arch': 'xtensawin', 'sysname': 'esp32', 'release': '1.16.0', 'name': 'micropython', 'mpy': 10757, 'version': '1.16.0', 'machine': 'ESP32 module with ESP32', 'build': '', 'nodename': 'esp32', 'platform': 'esp32', 'family': 'micropython'}
# Stubber: 1.3.9
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union


class Pin:
    """A pin object is used to control I/O pins (also known as GPIO - general-purpose
    input/output).  Pin objects are commonly associated with a physical pin that can
    drive an output voltage and read input voltages.  The pin class has methods to set the mode of
    the pin (IN, OUT, etc) and methods to get and set the digital logic level.
    For analog control of a pin, see the :class:`ADC` class.

    A pin object is constructed by using an identifier which unambiguously
    specifies a certain I/O pin.  The allowed forms of the identifier and the
    physical pin that the identifier maps to are port-specific.  Possibilities
    for the identifier are an integer, a string or a tuple with port and pin
    number.

    Usage Model::

        from machine import Pin

        # create an output pin on pin #0
        p0 = Pin(0, Pin.OUT)

        # set the value low then high
        p0.value(0)
        p0.value(1)

        # create an input pin on pin #2, with a pull up resistor
        p2 = Pin(2, Pin.IN, Pin.PULL_UP)

        # read and print the pin value
        print(p2.value())

        # reconfigure pin #0 in input mode with a pull down resistor
        p0.init(p0.IN, p0.PULL_DOWN)

        # configure an irq callback
        p0.irq(lambda p:print(p))
    """

    IN = 1
    IRQ_FALLING = 2
    IRQ_RISING = 1
    OPEN_DRAIN = 7
    OUT = 3
    PULL_DOWN = 1
    PULL_HOLD = 4
    PULL_UP = 2
    WAKE_HIGH = 5
    WAKE_LOW = 4

    def __init__(
        self, id, mode: int = -1, pull: int = -1, *, value: int = -1, drive=-1, alt=-1
    ) -> None:
        """Access the pin peripheral (GPIO pin) associated with the given ``id``.  If
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
        ...

    def init(self, mode: int = -1, pull: int = -1, *, value: int = -1, drive=-1, alt=-1) -> None:
        """Re-initialise the pin using the given parameters.  Only those arguments that
        are specified will be set.  The rest of the pin peripheral state will remain
        unchanged.  See the constructor documentation for details of the arguments.
        """

    def __call__(self, x: int) -> Union[int, None]:
        """Pin.__call__([x])

        Pin objects are callable.  The call method provides a (fast) shortcut to set
        and get the value of the pin.  It is equivalent to Pin.value([x]).
        See :meth:`Pin.value` for more details.
        """

    def irq(self, *argc) -> Any:

        ...

    def off(self) -> None:
        """Set pin to "0" output level"""
        ...

    def on(self) -> None:
        """Set pin to "1" output level"""
        ...

    def value(self, *argc) -> Union[int, None]:
        """This method allows to set and get the value of the pin, depending on whether
        the argument ``x`` is supplied or not.

        If the argument is omitted then this method gets the digital logic level of
        the pin, returning 0 or 1 corresponding to low and high voltage signals
        respectively.  The behaviour of this method depends on the mode of the pin:

            - ``Pin.IN`` - The method returns the actual input value currently present
            on the pin.
            - ``Pin.OUT`` - The behaviour and return value of the method is undefined.
            - ``Pin.OPEN_DRAIN`` - If the pin is in state '0' then the behaviour and
            return value of the method is undefined.  Otherwise, if the pin is in
            state '1', the method returns the actual input value currently present
            on the pin.

        If the argument is supplied then this method sets the digital logic level of
        the pin.  The argument ``x`` can be anything that converts to a boolean.
        If it converts to ``True``, the pin is set to state '1', otherwise it is set
        to state '0'.  The behaviour of this method depends on the mode of the pin:

            - ``Pin.IN`` - The value is stored in the output buffer for the pin.  The
            pin state does not change, it remains in the high-impedance state.  The
            stored value will become active on the pin as soon as it is changed to
            ``Pin.OUT`` or ``Pin.OPEN_DRAIN`` mode.
            - ``Pin.OUT`` - The output buffer is set to the given value immediately.
            - ``Pin.OPEN_DRAIN`` - If the value is '0' the pin is set to a low voltage
            state.  Otherwise the pin is set to high-impedance state.
        """
        ...


class ADC:
    """The ADC class provides an interface to analog-to-digital convertors, and
    represents a single endpoint that can sample a continuous voltage and
    convert it to a discretised value.

    On the ESP32 ADC functionality is available on Pins 32-39. Note that, when
    using the default configuration, input voltages on the ADC pin must be between
    0.0v and 1.0v (anything above 1.0v will just read as 4095).  Attenuation must
    be applied in order to increase this usable voltage range.

    Use the :ref:`machine.ADC <machine.ADC>` class::

        from machine import ADC

        adc = ADC(Pin(32))          # create ADC object on ADC pin
        adc.read()                  # read value, 0-4095 across voltage range 0.0v - 1.0v

        adc.atten(ADC.ATTN_11DB)    # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
        adc.width(ADC.WIDTH_9BIT)   # set 9 bit return values (returned range 0-511)
        adc.read()                  # read value using the newly configured attenuation and width

    Example usage::

        import machine

        adc = machine.ADC(pin)   # create an ADC object acting on a pin
        val = adc.read_u16()     # read a raw analog value in the range 0-65535
    """

    def __init__(self, id: Union[int, Pin, Any]) -> None:
        """Access the ADC associated with a source identified by *id*.  This
        *id* may be an integer (usually specifying a channel number), a
        :ref:`Pin <machine.Pin>` object, or other value supported by the
        underlying machine.
        """
        ...

    ATTN_0DB = 0
    ATTN_11DB = 3
    ATTN_2_5DB = 1
    ATTN_6DB = 2
    WIDTH_10BIT = 1
    WIDTH_11BIT = 2
    WIDTH_12BIT = 3
    WIDTH_9BIT = 0

    def atten(self, attenuation: int) -> Any:
        """This method allows for the setting of the amount of attenuation on the
        input of the ADC. This allows for a wider possible input voltage range,
        at the cost of accuracy (the same number of bits now represents a wider
        range). The possible attenuation options are:

        - ``ADC.ATTN_0DB``: 0dB attenuation, gives a maximum input voltage
            of 1.00v - this is the default configuration
        - ``ADC.ATTN_2_5DB``: 2.5dB attenuation, gives a maximum input voltage
            of approximately 1.34v
        - ``ADC.ATTN_6DB``: 6dB attenuation, gives a maximum input voltage
            of approximately 2.00v
        - ``ADC.ATTN_11DB``: 11dB attenuation, gives a maximum input voltage
            of approximately 3.6v

        .. Warning::
        Despite 11dB attenuation allowing for up to a 3.6v range, note that the
        absolute maximum voltage rating for the input pins is 3.6v, and so going
        near this boundary may be damaging to the IC!
        """
        ...

    def read(self) -> int:
        """Read the value on the analog pin and return it. The returned value will be between 0 and 4095."""
        ...

    def read_u16(self) -> int:
        """Take an analog reading and return an integer in the range 0-65535.
        The return value represents the raw reading taken by the ADC, scaled
        such that the minimum value is 0 and the maximum value is 65535.
        """
        ...

    def width(self, width: int) -> None:
        """This method allows for the setting of the number of bits to be utilised
        and returned during ADC reads. Possible width options are:

        - ``ADC.WIDTH_9BIT``: 9 bit data
        - ``ADC.WIDTH_10BIT``: 10 bit data
        - ``ADC.WIDTH_11BIT``: 11 bit data
        - ``ADC.WIDTH_12BIT``: 12 bit data - this is the default configuration
        """
        ...


class DAC:
    """The DAC is used to output analog values (a specific voltage) on pin X5 or pin X6.
    The voltage will be between 0 and 3.3V.

    *This module will undergo changes to the API.*
    To output a continuous sine-wave::

        import math
        from pyb import DAC

        # create a buffer containing a sine-wave
        buf = bytearray(100)
        for i in range(len(buf)):
            buf[i] = 128 + int(127 * math.sin(2 * math.pi * i / len(buf)))

        # output the sine-wave at 400Hz
        dac = DAC(1)
        dac.write_timed(buf, 400 * len(buf), mode=DAC.CIRCULAR)

    To output a continuous sine-wave at 12-bit resolution::

        import math
        from array import array
        from pyb import DAC

        # create a buffer containing a sine-wave, using half-word samples
        buf = array('H', 2048 + int(2047 * math.sin(2 * math.pi * i / 128)) for i in range(128))

        # output the sine-wave at 400Hz
        dac = DAC(1, bits=12)
        dac.write_timed(buf, 400 * len(buf), mode=DAC.CIRCULAR)
    """

    def __init__(self, port: Union[Pin], bits=8, *, buffering: Union[bool, None] = None) -> None:
        """Construct a new DAC object.

        *ESP32*
        ``port`` can be a pin object

        *pyboard*
        ``port`` can be a pin object, or an integer (1 or 2).
        DAC(1) is on pin X5 and DAC(2) is on pin X6.

        ``bits`` is an integer specifying the resolution, and can be 8 or 12.
        The maximum value for the write (and write_timed methods) will be
        2\*\*``bits``-1.

        The *buffering* parameter selects the behaviour of the DAC op-amp output
        buffer, whose purpose is to reduce the output impedance.  It can be
        ``None`` to select the default (buffering enabled for :meth:`DAC.noise`,
        :meth:`DAC.triangle` and :meth:`DAC.write_timed`, and disabled for
        :meth:`DAC.write`), ``False`` to disable buffering completely, or ``True``
        to enable output buffering.

        When buffering is enabled the DAC pin can drive loads down to 5K Ohm.
        Otherwise it has an output impedance of 15KÎ© maximum: consequently
        to achieve a 1% accuracy without buffering requires the applied load
        to be less than 1.5MÎ©.  Using the buffer incurs a penalty in accuracy,
        especially near the extremes of range.
        """

    def write(self, value) -> Any:
        """Direct access to the DAC output.  The minimum value is 0.  The maximum
        value is 2\*\*``bits``-1, where ``bits`` is set when creating the DAC
        object or by using the ``init`` method.
        """
        ...


DEEPSLEEP = 4
DEEPSLEEP_RESET = 4
EXT0_WAKE = 2
EXT1_WAKE = 3
HARD_RESET = 2


class I2C:
    """
    class I2C -- a two-wire serial protocol
    =======================================

    I2C is a two-wire protocol for communicating between devices.  At the physical
    level it consists of 2 wires: SCL and SDA, the clock and data lines respectively.

    I2C objects are created attached to a specific bus.  They can be initialised
    when created, or initialised later on.

    Printing the I2C object gives you information about its configuration.

    Both hardware and software I2C implementations exist via the
    :ref:`machine.I2C <machine.I2C>` and `machine.SoftI2C` classes.  Hardware I2C uses
    underlying hardware support of the system to perform the reads/writes and is
    usually efficient and fast but may have restrictions on which pins can be used.
    Software I2C is implemented by bit-banging and can be used on any pin but is not
    as efficient.  These classes have the same methods available and differ primarily
    in the way they are constructed.

    https://docs.micropython.org/en/latest/library/machine.I2C.html
    """

    # https://docs.micropython.org/en/latest/_sources/library/machine.I2C.rst.txt

    def __init__(self, id, *, scl: Pin, sda: Pin, freq: int) -> None:
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
        ...

    def readfrom(self, addr, nbytes, stop=True, /) -> bytes:
        """
        Read *nbytes* from the slave specified by *addr*.
        If *stop* is true then a STOP condition is generated at the end of the transfer.
        Returns a `bytes` object with the data read.
        """
        ...

    def readfrom_into(self, *argc) -> None:
        """
        Read into *buf* from the slave specified by *addr*.
        The number of bytes read will be the length of *buf*.
        If *stop* is true then a STOP condition is generated at the end of the transfer.

        The method returns ``None``.
        """
        ...

    def readfrom_mem(self, addr, memaddr, nbytes, *, addrsize=8) -> bytes:
        """
        Read *nbytes* from the slave specified by *addr* starting from the memory
        address specified by *memaddr*.
        The argument *addrsize* specifies the address size in bits.
        Returns a `bytes` object with the data read.
        """
        ...

    def readfrom_mem_into(self, addr, memaddr, buf, *, addrsize=8) -> None:
        """
        Read into *buf* from the slave specified by *addr* starting from the
        memory address specified by *memaddr*.  The number of bytes read is the
        length of *buf*.
        The argument *addrsize* specifies the address size in bits (on ESP8266
        this argument is not recognised and the address size is always 8 bits).

        The method returns ``None``.
        """

        ...

    def readinto(self, buf, nack=True, /) -> None:
        """
        Reads bytes from the bus and stores them into *buf*.  The number of bytes
        read is the length of *buf*.  An ACK will be sent on the bus after
        receiving all but the last byte.  After the last byte is received, if *nack*
        is true then a NACK will be sent, otherwise an ACK will be sent (and in this
        case the slave assumes more bytes are going to be read in a later call)
        """

        ...

    def scan(self) -> List[int]:
        """
        Scan all I2C addresses between 0x08 and 0x77 inclusive and return a list of
        those that respond.  A device responds if it pulls the SDA line low after
        its address (including a write bit) is sent on the bus.

        """
        ...

    def start(self) -> None:
        """Generate a START condition on the bus (SDA transitions to low while SCL is high)."""
        ...

    def stop(self) -> None:
        """Generate a STOP condition on the bus (SDA transitions to high while SCL is high)"""

        ...

    def write(self, buf) -> Any:
        """
        Write the bytes from *buf* to the bus.  Checks that an ACK is received
        after each byte and stops transmitting the remaining bytes if a NACK is
        received.  The function returns the number of ACKs that were received.
        """

        ...

    def writeto(self, addr, buf, stop=True, /) -> Any:
        """
        Write the bytes from *buf* to the slave specified by *addr*.  If a
        NACK is received following the write of a byte from *buf* then the
        remaining bytes are not sent.  If *stop* is true then a STOP condition is
        generated at the end of the transfer, even if a NACK is received.
        The function returns the number of ACKs that were received.
        """

        ...

    def writeto_mem(self, addr, memaddr, buf, *, addrsize=8) -> None:
        """
        Write *buf* to the slave specified by *addr* starting from the
        memory address specified by *memaddr*.
        The argument *addrsize* specifies the address size in bits (on ESP8266
        this argument is not recognised and the address size is always 8 bits).

        The method returns ``None``.
        """
        ...

    def writevto(self, addr, vector, stop=True, /) -> int:
        """
        Write the bytes contained in *vector* to the slave specified by *addr*.
        *vector* should be a tuple or list of objects with the buffer protocol.
        The *addr* is sent once and then the bytes from each object in *vector*
        are written out sequentially.  The objects in *vector* may be zero bytes
        in length in which case they don't contribute to the output.

        If a NACK is received following the write of a byte from one of the
        objects in *vector* then the remaining bytes, and any remaining objects,
        are not sent.  If *stop* is true then a STOP condition is generated at
        the end of the transfer, even if a NACK is received.  The function
        returns the number of ACKs that were received.
        """
        ...

    def deinit(self) -> None:
        """
        Turn off the I2C bus.
        Availability: WiPy.
        """
        ...


class SoftI2C(I2C):
    def __init__(self, scl, sda, *, freq=400000, timeout=255) -> None:
        """
        Construct a new software I2C object.  The parameters are:

           - *scl* should be a pin object specifying the pin to use for SCL.
           - *sda* should be a pin object specifying the pin to use for SDA.
           - *freq* should be an integer which sets the maximum frequency
             for SCL.
           - *timeout* is the maximum time in microseconds to wait for clock
             stretching (SCL held low by another device on the bus), after
             which an ``OSError(ETIMEDOUT)`` exception is raised.
        """
        ...


PIN_WAKE = 2


class PWM:
    """
    class PWM -- pulse width modulation
    ===================================
    This class provides pulse width modulation output.

    Example usage::

    from machine import PWM

    pwm = PWM(pin)          # create a PWM object on a pin
    pwm.duty_u16(32768)     # set duty to 50%

    # reinitialise with a period of 200us, duty of 5us
    pwm.init(freq=5000, duty_ns=5000)

    pwm.duty_ns(3000)       # set pulse width to 3us

    pwm.deinit()
    """

    def __init__(self, dest, *, freq, duty_u16, duty_ns) -> None:
        # BUG: docbug in prototype /*

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
        ...

    def init(self, *, freq, duty_u16, duty_ns) -> None:
        # bug: dogbug \* in documentation
        # todo: init is not detected/dumped by stubber
        """
        Modify settings for the PWM object.  See the above constructor for details
        about the parameters.
        """
        ...

    def deinit(self) -> None:
        "Disable the PWM output."
        ...

    def duty(self, value: Optional[int]) -> Any:
        """
        Get or set the current duty cycle of the PWM output, as an unsigned 16-bit
        value in the range 0 to 65535 inclusive.

        With no arguments the duty cycle is returned.

        With a single *value* argument the duty cycle is set to that value, measured
        as the ratio ``value / 65535``.
        """
        ...

    def freq(self, value: Optional[int]) -> Any:
        # todo: add conditional type comments
        """
        Get or set the current frequency of the PWM output.

        With no arguments the frequency in Hz is returned.

        With a single *value* argument the frequency is set to that value in Hz.  The
        method may raise a ``ValueError`` if the frequency is outside the valid range.
        """
        ...

    def duty_ns(self, value: Optional[int]) -> Any:
        """
        Get or set the current pulse width of the PWM output, as a value in nanoseconds.

        With no arguments the pulse width in nanoseconds is returned.

        With a single *value* argument the pulse width is set to that value.
        """
        ...


PWRON_RESET = 1


class RTC:
    """"""

    def datetime(self, *argc) -> Any:

        ...

    def init(self, *argc) -> Any:

        ...

    def memory(self, *argc) -> Any:

        ...


class SDCard:
    """"""

    def deinit(self, *argc) -> Any:

        ...

    def info(self, *argc) -> Any:

        ...

    def ioctl(self, *argc) -> Any:

        ...

    def readblocks(self, *argc) -> Any:

        ...

    def writeblocks(self, *argc) -> Any:

        ...


SLEEP = 2
SOFT_RESET = 5


class SPI:
    """"""

    LSB = 1
    MSB = 0

    def __init__(
        self,
        id,
        baudrate: int,
        *,
        polarity: int = 0,
        phase: int = 0,
        bits: int = 8,
        firstbit: int = MSB,
        sck: Pin = None,
        mosi: Pin = None,
        miso: Pin = None,
    ) -> None:
        """Construct an SPI object on the given bus, id. Values of id depend on a particular port and its hardware.
        Values 0, 1, etc. are commonly used to select hardware SPI block #0, #1, etc.
        With no additional parameters, the SPI object is created but not initialised (it has the settings from the last
        initialisation of the bus, if any). If extra arguments are given, the bus is initialised.
        See init for parameters of initialisation.
        """
        ...

    def init(
        self,
        baudrate: int,
        *,
        polarity: int = 0,
        phase: int = 0,
        bits: int = 8,
        firstbit: int = MSB,
        sck: Pin = None,
        mosi: Pin = None,
        miso: Pin = None,
    ) -> Any:
        """Initialise the SPI bus with the given parameters:

        Parameters
        ----------
        * baudrate is the SCK clock rate.
        * polarity can be 0 or 1, and is the level the idle clock line sits at.
        * phase can be 0 or 1 to sample data on the first or second clock edge respectively.
        * bits is the width in bits of each transfer. Only 8 is guaranteed to be supported by all hardware.
        * firstbit can be SPI.MSB or SPI.LSB.
        * sck, mosi, miso are pins (machine.Pin) objects to use for bus signals. For most hardware SPI blocks (as selected by id parameter to the constructor), pins are fixed and cannot be changed. In some cases, hardware blocks allow 2-3 alternative pin sets for a hardware SPI block. Arbitrary pin assignments are possible only for a bitbanging SPI driver (id = -1).

        Notes
        -----
        In the case of hardware SPI the actual clock frequency may be lower than the requested baudrate. This is dependant on the platform hardware. The actual rate may be determined by printing the SPI object.

        """
        ...

    def deinit(self) -> None:
        """Turn off the SPI bus."""
        ...

    def read(self, nbytes: int, write: int = 0) -> bytes:
        ...

    def readinto(self, buf: bytes, write: int = 0) -> None:
        ...

    def write(self, buf: bytes) -> None:

        ...

    def write_readinto(self, write_buf: bytes, read_buf: bytes) -> None:
        ...


class Signal:
    """"""

    def off(self, *argc) -> Any:

        ...

    def on(self, *argc) -> Any:

        ...

    def value(self, *argc) -> Any:

        ...


class SoftSPI:
    """"""

    LSB = 1
    MSB = 0

    def deinit(self, *argc) -> Any:

        ...

    def init(self, *argc) -> Any:

        ...

    def read(self, *argc) -> Any:

        ...

    def readinto(self, *argc) -> Any:

        ...

    def write(self, *argc) -> Any:

        ...

    def write_readinto(self, *argc) -> Any:

        ...


TIMER_WAKE = 4
TOUCHPAD_WAKE = 5


class Timer:
    """"""

    ONE_SHOT = 0
    PERIODIC = 1

    def deinit(self, *argc) -> Any:

        ...

    def init(self, *argc) -> Any:

        ...

    def value(self, *argc) -> Any:

        ...


class TouchPad:
    """"""

    def config(self, *argc) -> Any:

        ...

    def read(self, *argc) -> Any:

        ...


class UART:
    """"""

    INV_CTS = 8
    INV_RTS = 64
    INV_RX = 4
    INV_TX = 32

    def any(self, *argc) -> Any:

        ...

    def deinit(self, *argc) -> Any:

        ...

    def init(self, *argc) -> Any:

        ...

    def read(self, *argc) -> Any:

        ...

    def readinto(self, *argc) -> Any:

        ...

    def readline(self, *argc) -> Any:

        ...

    def sendbreak(self, *argc) -> Any:

        ...

    def write(self, *argc) -> Any:

        ...


ULP_WAKE = 6


class WDT:
    """"""

    def feed(*argc) -> Any:

        ...


WDT_RESET = 3


def deepsleep(time_ms: Optional[int]) -> None:
    """Stops execution in an attempt to enter a low power state.

    If *time_ms* is specified then this will be the maximum time in milliseconds that
    the sleep will last for.  Otherwise the sleep can last indefinitely.

    With or without a timeout, execution may resume at any time if there are events
    that require processing.  Such events, or wake sources, should be configured before
    sleeping, like `Pin` change or `RTC` timeout.

    The precise behaviour and power-saving capabilities of lightsleep and deepsleep is
    highly dependent on the underlying hardware, but the general properties are:

    * A lightsleep has full RAM and state retention.  Upon wake execution is resumed
      from the point where the sleep was requested, with all subsystems operational.

    * A deepsleep may not retain RAM or any other state of the system (for example
      peripherals or network interfaces).  Upon wake execution is resumed from the main
      script, similar to a hard or power-on reset. The `reset_cause()` function will
      return `machine.DEEPSLEEP` and this can be used to distinguish a deepsleep wake
    """
    ...


def disable_irq() -> None:
    """Disable interrupt requests.
    Returns the previous IRQ state which should be considered an opaque value.
    This return value should be passed to the `enable_irq()` function to restore
    interrupts to their original state, before `disable_irq()` was called.
    """
    ...


def enable_irq() -> None:
    """Re-enable interrupt requests.
    The *state* parameter should be the value that was returned from the most
    recent call to the `disable_irq()` function.
    """
    ...


def freq(int) -> int:
    """Returns the CPU frequency in hertz. (Generic)
    On some ports this can also be used to set the CPU frequency by ...ing in *hz*.
    """
    ...


def idle() -> None:
    """Gates the clock to the CPU, useful to reduce power consumption at any time during
    short or long periods. Peripherals continue working and execution resumes as soon
    as any interrupt is triggered (on many ports this includes system timer
    interrupt occurring at regular intervals on the order of millisecond).
    """
    ...


def lightsleep(time_ms: Optional[int]) -> None:
    """Stops execution in an attempt to enter a low power state.

    If *time_ms* is specified then this will be the maximum time in milliseconds that
    the sleep will last for.  Otherwise the sleep can last indefinitely.

    With or without a timeout, execution may resume at any time if there are events
    that require processing.  Such events, or wake sources, should be configured before
    sleeping, like `Pin` change or `RTC` timeout.

    The precise behaviour and power-saving capabilities of lightsleep and deepsleep is
    highly dependent on the underlying hardware, but the general properties are:

    * A lightsleep has full RAM and state retention.  Upon wake execution is resumed
      from the point where the sleep was requested, with all subsystems operational.

    * A deepsleep may not retain RAM or any other state of the system (for example
      peripherals or network interfaces).  Upon wake execution is resumed from the main
      script, similar to a hard or power-on reset. The `reset_cause()` function will
      return `machine.DEEPSLEEP` and this can be used to distinguish a deepsleep wake
    """
    ...


mem16 = None
mem32 = None
mem8 = None


def reset() -> None:
    """Resets the device in a manner similar to pushing the external RESET button."""
    ...


def reset_cause() -> Any:
    """Get the reset cause. See :ref:`constants <machine_constants>` for the possible return values."""

    ...


def sleep() -> None:
    "note:: This function is deprecated, use `lightsleep()` instead with no arguments"
    ...


def soft_reset() -> None:
    """Performs a soft reset of the interpreter, deleting all Python objects and
    resetting the Python heap.  It tries to retain the method by which the user
    is connected to the MicroPython REPL (eg serial, USB, Wifi).
    """
    ...


# def time_pulse_us(__pin: Pin, pulse_level: int, timeout_us: int = 1000000, /) -> int:
def time_pulse_us(pin: Pin, pulse_level: int, timeout_us: int = 1000000) -> int:
    """Time a pulse on the given *pin*, and return the duration of the pulse in
    microseconds.  The *pulse_level* argument should be 0 to time a low pulse
    or 1 to time a high pulse.

    If the current input value of the pin is different to *pulse_level*,
    the function first (*) waits until the pin input becomes equal to *pulse_level*,
    then (**) times the duration that the pin is equal to *pulse_level*.
    If the pin is already equal to *pulse_level* then timing starts straight away.

    The function will return -2 if there was timeout waiting for condition marked
    (*) above, and -1 if there was timeout during the main measurement, marked (**)
    above. The timeout is the same for both cases and given by *timeout_us* (which
    is in microseconds).
    """
    ...


def unique_id() -> bytes:
    """Returns a byte string with a unique identifier of a board/SoC. It will vary
    from a board/SoC instance to another, if underlying hardware allows. Length
    varies by hardware (so use substring of a full value if you expect a short
    ID). In some MicroPython ports, ID corresponds to the network MAC address.
    """
    ...


def wake_reason() -> Any:
    """Get the wake reason. See :ref:`constants <machine_constants>` for the possible return values.
    Availability: ESP32, WiPy.
    """
    ...
