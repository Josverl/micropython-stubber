""" """

from __future__ import annotations

from typing import Callable, Union, overload

from _mpy_shed import _IRQ, AnyReadableBuf, AnyWritableBuf
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

from .Pin import Pin

class UART:
    """
    UART implements the standard UART/USART duplex serial communications protocol.  At
    the physical level it consists of 2 lines: RX and TX.  The unit of communication
    is a character (not to be confused with a string character) which can be 8 or 9
    bits wide.

    UART objects can be created and initialised using::

        from machine import UART

        uart = UART(1, 9600)                         # init with given baudrate
        uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters

    Supported parameters differ on a board:

    Pyboard: Bits can be 7, 8 or 9. Stop can be 1 or 2. With *parity=None*,
    only 8 and 9 bits are supported.  With parity enabled, only 7 and 8 bits
    are supported.

    WiPy/CC3200: Bits can be 5, 6, 7, 8. Stop can be 1 or 2.

    A UART object acts like a `stream` object and reading and writing is done
    using the standard stream methods::

        uart.read(10)       # read 10 characters, returns a bytes object
        uart.read()         # read all available characters
        uart.readline()     # read a line
        uart.readinto(buf)  # read and store into the given buffer
        uart.write('abc')   # write the 3 characters
    """

    RTS: Incomplete
    """\
    Flow control options.
    
    Availability: esp32, mimxrt, renesas-ra, rp2, stm32.
    """
    CTS: Incomplete
    """\
    Flow control options.
    
    Availability: esp32, mimxrt, renesas-ra, rp2, stm32.
    """
    IRQ_RXIDLE: Incomplete
    """\
    IRQ trigger sources.
    
    Availability: renesas-ra, stm32, esp32, rp2040, mimxrt, samd, cc3200.
    """
    IRQ_RX: Incomplete
    """\
    IRQ trigger sources.
    
    Availability: renesas-ra, stm32, esp32, rp2040, mimxrt, samd, cc3200.
    """
    IRQ_TXIDLE: Incomplete
    """\
    IRQ trigger sources.
    
    Availability: renesas-ra, stm32, esp32, rp2040, mimxrt, samd, cc3200.
    """
    IRQ_BREAK: Incomplete
    """\
    IRQ trigger sources.
    
    Availability: renesas-ra, stm32, esp32, rp2040, mimxrt, samd, cc3200.
    """
    @overload
    def __init__(
        self,
        id: int | str,
        baudrate: int = 9600,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        /,
        *,
        tx: Pin | None = None,
        rx: Pin | None = None,
        txbuf: int | None = None,
        rxbuf: int | None = None,
        timeout: int | None = None,
        timeout_char: int | None = None,
        invert: int | None = None,
    ):
        """
        Construct a UART object of the given id.
        """

    @overload
    def __init__(
        self,
        id: int | str,
        baudrate: int = 9600,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        /,
        *,
        pins: tuple[Pin, Pin] | None = None,
    ):
        """
        Construct a UART object of the given id.
        """

    @overload
    def __init__(
        self,
        id: int | str,
        baudrate: int = 9600,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        /,
        *,
        pins: tuple[Pin, Pin, Pin, Pin] | None = None,
    ):
        """
        Construct a UART object of the given id.
        """

    @overload
    def init(
        self,
        baudrate: int = 9600,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        /,
        *,
        tx: Pin | None = None,
        rx: Pin | None = None,
        txbuf: int | None = None,
        rxbuf: int | None = None,
        timeout: int | None = None,
        timeout_char: int | None = None,
        invert: int | None = None,
    ) -> None:
        """
        Initialise the UART bus with the given parameters:

          - *baudrate* is the clock rate.
          - *bits* is the number of bits per character, 7, 8 or 9.
          - *parity* is the parity, ``None``, 0 (even) or 1 (odd).
          - *stop* is the number of stop bits, 1 or 2.

        Additional keyword-only parameters that may be supported by a port are:

          - *tx* specifies the TX pin to use.
          - *rx* specifies the RX pin to use.
          - *rts* specifies the RTS (output) pin to use for hardware receive flow control.
          - *cts* specifies the CTS (input) pin to use for hardware transmit flow control.
          - *txbuf* specifies the length in characters of the TX buffer.
          - *rxbuf* specifies the length in characters of the RX buffer.
          - *timeout* specifies the time to wait for the first character (in ms).
          - *timeout_char* specifies the time to wait between characters (in ms).
          - *invert* specifies which lines to invert.

              - ``0`` will not invert lines (idle state of both lines is logic high).
              - ``UART.INV_TX`` will invert TX line (idle state of TX line now logic low).
              - ``UART.INV_RX`` will invert RX line (idle state of RX line now logic low).
              - ``UART.INV_TX | UART.INV_RX`` will invert both lines (idle state at logic low).

          - *flow* specifies which hardware flow control signals to use. The value
            is a bitmask.

              - ``0`` will ignore hardware flow control signals.
              - ``UART.RTS`` will enable receive flow control by using the RTS output pin to
                signal if the receive FIFO has sufficient space to accept more data.
              - ``UART.CTS`` will enable transmit flow control by pausing transmission when the
                CTS input pin signals that the receiver is running low on buffer space.
              - ``UART.RTS | UART.CTS`` will enable both, for full hardware flow control.

        On the WiPy only the following keyword-only parameter is supported:

          - *pins* is a 4 or 2 item list indicating the TX, RX, RTS and CTS pins (in that order).
            Any of the pins can be None if one wants the UART to operate with limited functionality.
            If the RTS pin is given the the RX pin must be given as well. The same applies to CTS.
            When no pins are given, then the default set of TX and RX pins is taken, and hardware
            flow control will be disabled. If *pins* is ``None``, no pin assignment will be made.

        .. note::
          It is possible to call ``init()`` multiple times on the same object in
          order to reconfigure  UART on the fly. That allows using single UART
          peripheral to serve different devices attached to different GPIO pins.
          Only one device can be served at a time in that case.
          Also do not call ``deinit()`` as it will prevent calling ``init()``
          again.
        """

    @overload
    def init(
        self,
        baudrate: int = 9600,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        /,
        *,
        pins: tuple[Pin, Pin] | None = None,
    ) -> None:
        """
        Initialise the UART bus with the given parameters:

          - *baudrate* is the clock rate.
          - *bits* is the number of bits per character, 7, 8 or 9.
          - *parity* is the parity, ``None``, 0 (even) or 1 (odd).
          - *stop* is the number of stop bits, 1 or 2.

        Additional keyword-only parameters that may be supported by a port are:

          - *tx* specifies the TX pin to use.
          - *rx* specifies the RX pin to use.
          - *rts* specifies the RTS (output) pin to use for hardware receive flow control.
          - *cts* specifies the CTS (input) pin to use for hardware transmit flow control.
          - *txbuf* specifies the length in characters of the TX buffer.
          - *rxbuf* specifies the length in characters of the RX buffer.
          - *timeout* specifies the time to wait for the first character (in ms).
          - *timeout_char* specifies the time to wait between characters (in ms).
          - *invert* specifies which lines to invert.

              - ``0`` will not invert lines (idle state of both lines is logic high).
              - ``UART.INV_TX`` will invert TX line (idle state of TX line now logic low).
              - ``UART.INV_RX`` will invert RX line (idle state of RX line now logic low).
              - ``UART.INV_TX | UART.INV_RX`` will invert both lines (idle state at logic low).

          - *flow* specifies which hardware flow control signals to use. The value
            is a bitmask.

              - ``0`` will ignore hardware flow control signals.
              - ``UART.RTS`` will enable receive flow control by using the RTS output pin to
                signal if the receive FIFO has sufficient space to accept more data.
              - ``UART.CTS`` will enable transmit flow control by pausing transmission when the
                CTS input pin signals that the receiver is running low on buffer space.
              - ``UART.RTS | UART.CTS`` will enable both, for full hardware flow control.

        On the WiPy only the following keyword-only parameter is supported:

          - *pins* is a 4 or 2 item list indicating the TX, RX, RTS and CTS pins (in that order).
            Any of the pins can be None if one wants the UART to operate with limited functionality.
            If the RTS pin is given the the RX pin must be given as well. The same applies to CTS.
            When no pins are given, then the default set of TX and RX pins is taken, and hardware
            flow control will be disabled. If *pins* is ``None``, no pin assignment will be made.

        .. note::
          It is possible to call ``init()`` multiple times on the same object in
          order to reconfigure  UART on the fly. That allows using single UART
          peripheral to serve different devices attached to different GPIO pins.
          Only one device can be served at a time in that case.
          Also do not call ``deinit()`` as it will prevent calling ``init()``
          again.
        """

    @overload
    def init(
        self,
        baudrate: int = 9600,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        /,
        *,
        pins: tuple[Pin, Pin, Pin, Pin] | None = None,
    ) -> None:
        """
        Initialise the UART bus with the given parameters:

          - *baudrate* is the clock rate.
          - *bits* is the number of bits per character, 7, 8 or 9.
          - *parity* is the parity, ``None``, 0 (even) or 1 (odd).
          - *stop* is the number of stop bits, 1 or 2.

        Additional keyword-only parameters that may be supported by a port are:

          - *tx* specifies the TX pin to use.
          - *rx* specifies the RX pin to use.
          - *rts* specifies the RTS (output) pin to use for hardware receive flow control.
          - *cts* specifies the CTS (input) pin to use for hardware transmit flow control.
          - *txbuf* specifies the length in characters of the TX buffer.
          - *rxbuf* specifies the length in characters of the RX buffer.
          - *timeout* specifies the time to wait for the first character (in ms).
          - *timeout_char* specifies the time to wait between characters (in ms).
          - *invert* specifies which lines to invert.

              - ``0`` will not invert lines (idle state of both lines is logic high).
              - ``UART.INV_TX`` will invert TX line (idle state of TX line now logic low).
              - ``UART.INV_RX`` will invert RX line (idle state of RX line now logic low).
              - ``UART.INV_TX | UART.INV_RX`` will invert both lines (idle state at logic low).

          - *flow* specifies which hardware flow control signals to use. The value
            is a bitmask.

              - ``0`` will ignore hardware flow control signals.
              - ``UART.RTS`` will enable receive flow control by using the RTS output pin to
                signal if the receive FIFO has sufficient space to accept more data.
              - ``UART.CTS`` will enable transmit flow control by pausing transmission when the
                CTS input pin signals that the receiver is running low on buffer space.
              - ``UART.RTS | UART.CTS`` will enable both, for full hardware flow control.

        On the WiPy only the following keyword-only parameter is supported:

          - *pins* is a 4 or 2 item list indicating the TX, RX, RTS and CTS pins (in that order).
            Any of the pins can be None if one wants the UART to operate with limited functionality.
            If the RTS pin is given the the RX pin must be given as well. The same applies to CTS.
            When no pins are given, then the default set of TX and RX pins is taken, and hardware
            flow control will be disabled. If *pins* is ``None``, no pin assignment will be made.

        .. note::
          It is possible to call ``init()`` multiple times on the same object in
          order to reconfigure  UART on the fly. That allows using single UART
          peripheral to serve different devices attached to different GPIO pins.
          Only one device can be served at a time in that case.
          Also do not call ``deinit()`` as it will prevent calling ``init()``
          again.
        """

    def deinit(self) -> None:
        """
        Turn off the UART bus.

        .. note::
          You will not be able to call ``init()`` on the object after ``deinit()``.
          A new instance needs to be created in that case.
        """
        ...

    def any(self) -> int:
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

    @overload
    def read(self) -> bytes | None:
        """
        Read characters.  If ``nbytes`` is specified then read at most that many bytes,
        otherwise read as much data as possible. It may return sooner if a timeout
        is reached. The timeout is configurable in the constructor.

        Return value: a bytes object containing the bytes read in.  Returns ``None``
        on timeout.
        """

    @overload
    def read(self, nbytes: int, /) -> bytes | None:
        """
        Read characters.  If ``nbytes`` is specified then read at most that many bytes,
        otherwise read as much data as possible. It may return sooner if a timeout
        is reached. The timeout is configurable in the constructor.

        Return value: a bytes object containing the bytes read in.  Returns ``None``
        on timeout.
        """

    @overload
    def readinto(self, buf: AnyWritableBuf, /) -> int | None:
        """
        Read bytes into the ``buf``.  If ``nbytes`` is specified then read at most
        that many bytes.  Otherwise, read at most ``len(buf)`` bytes. It may return sooner if a timeout
        is reached. The timeout is configurable in the constructor.

        Return value: number of bytes read and stored into ``buf`` or ``None`` on
        timeout.
        """

    @overload
    def readinto(self, buf: AnyWritableBuf, nbytes: int, /) -> int | None:
        """
        Read bytes into the ``buf``.  If ``nbytes`` is specified then read at most
        that many bytes.  Otherwise, read at most ``len(buf)`` bytes. It may return sooner if a timeout
        is reached. The timeout is configurable in the constructor.

        Return value: number of bytes read and stored into ``buf`` or ``None`` on
        timeout.
        """

    def readline(self) -> Union[str, None]:
        """
        Read a line, ending in a newline character. It may return sooner if a timeout
        is reached. The timeout is configurable in the constructor.

        Return value: the line read or ``None`` on timeout.
        """
        ...

    def write(self, buf: AnyReadableBuf, /) -> Union[int, None]:
        """
        Write the buffer of bytes to the bus.

        Return value: number of bytes written or ``None`` on timeout.
        """
        ...

    def sendbreak(self) -> None:
        """
        Send a break condition on the bus. This drives the bus low for a duration
        longer than required for a normal transmission of a character.
        """
        ...

    def flush(self) -> Incomplete:
        """
        Waits until all data has been sent. In case of a timeout, an exception is raised. The timeout
        duration depends on the tx buffer size and the baud rate. Unless flow control is enabled, a timeout
        should not occur.

        .. note::

            For the esp8266 and nrf ports the call returns while the last byte is sent.
            If required, a one character wait time has to be added in the calling script.

        Availability: rp2, esp32, esp8266, mimxrt, cc3200, stm32, nrf ports, renesas-ra
        """
        ...

    def txdone(self) -> bool:
        """
        Tells whether all data has been sent or no data transfer is happening. In this case,
        it returns ``True``. If a data transmission is ongoing it returns ``False``.

        .. note::

            For the esp8266 and nrf ports the call may return ``True`` even if the last byte
            of a transfer is still being sent. If required, a one character wait time has to be
            added in the calling script.

        Availability: rp2, esp32, esp8266, mimxrt, cc3200, stm32, nrf ports, renesas-ra
        """
        ...

    def irq(
        self,
        trigger: int,
        priority: int = 1,
        handler: Callable[[UART], None] | None = None,
        wake: int = IDLE,
        /,
    ) -> _IRQ:
        """
        Configure an interrupt handler to be called when a UART event occurs.

        The arguments are:

          - *handler* is an optional function to be called when the interrupt event
            triggers.  The handler must take exactly one argument which is the
            ``UART`` instance.

          - *trigger* configures the event(s) which can generate an interrupt.
            Possible values are a mask of one or more of the following:

            - ``UART.IRQ_RXIDLE`` interrupt after receiving at least one character
              and then the RX line goes idle.
            - ``UART.IRQ_RX`` interrupt after each received character.
            - ``UART.IRQ_TXIDLE`` interrupt after or while the last character(s) of
              a message are or have been sent.
            - ``UART.IRQ_BREAK`` interrupt when a break state is detected at RX

          - *hard* if true a hardware interrupt is used.  This reduces the delay
            between the pin change and the handler being called. Hard interrupt
            handlers may not allocate memory; see :ref:`isr_rules`.

        Returns an irq object.

        Due to limitations of the hardware not all trigger events are available on all ports.
        """
        ...
