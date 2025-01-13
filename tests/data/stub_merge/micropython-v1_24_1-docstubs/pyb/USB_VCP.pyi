""" """

from __future__ import annotations

from array import array
from typing import List, overload

from _mpy_shed import AnyReadableBuf, AnyWritableBuf
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

class USB_VCP:
    """
    The USB_VCP class allows creation of a `stream`-like object representing the USB
    virtual comm port.  It can be used to read and write data over USB to
    the connected host.
    """

    RTS: Incomplete
    """to select the flow control type."""
    CTS: Incomplete
    """to select the flow control type."""
    IRQ_RX: Incomplete
    """IRQ trigger values for :meth:`USB_VCP.irq`."""
    def __init__(self, id: int = 0, /) -> None:
        """
        Create a new USB_VCP object.  The *id* argument specifies which USB VCP port to
        use.
        """

    def init(self, *, flow: int = -1) -> None:
        """
        Configure the USB VCP port.  If the *flow* argument is not -1 then the value sets
        the flow control, which can be a bitwise-or of ``USB_VCP.RTS`` and ``USB_VCP.CTS``.
        RTS is used to control read behaviour and CTS, to control write behaviour.
        """
        ...

    def setinterrupt(self, chr: int, /) -> None:
        """
        Set the character which interrupts running Python code.  This is set
        to 3 (CTRL-C) by default, and when a CTRL-C character is received over
        the USB VCP port, a KeyboardInterrupt exception is raised.

        Set to -1 to disable this interrupt feature.  This is useful when you
        want to send raw bytes over the USB VCP port.
        """
        ...

    def isconnected(self) -> bool:
        """
        Return ``True`` if USB is connected as a serial device, else ``False``.
        """
        ...

    def any(self) -> bool:
        """
        Return ``True`` if any characters waiting, else ``False``.
        """
        ...

    def close(self) -> None:
        """
        This method does nothing.  It exists so the USB_VCP object can act as
        a file.
        """
        ...

    @overload
    def read(self) -> bytes | None:
        """
        Read at most ``nbytes`` from the serial device and return them as a
        bytes object.  If ``nbytes`` is not specified then the method reads
        all available bytes from the serial device.
        USB_VCP `stream` implicitly works in non-blocking mode,
        so if no pending data available, this method will return immediately
        with ``None`` value.
        """

    @overload
    def read(self, nbytes, /) -> bytes | None:
        """
        Read at most ``nbytes`` from the serial device and return them as a
        bytes object.  If ``nbytes`` is not specified then the method reads
        all available bytes from the serial device.
        USB_VCP `stream` implicitly works in non-blocking mode,
        so if no pending data available, this method will return immediately
        with ``None`` value.
        """

    @overload
    def readinto(self, buf: AnyWritableBuf, /) -> int | None:
        """
        Read bytes from the serial device and store them into ``buf``, which
        should be a buffer-like object.  At most ``len(buf)`` bytes are read.
        If ``maxlen`` is given and then at most ``min(maxlen, len(buf))`` bytes
        are read.

        Returns the number of bytes read and stored into ``buf`` or ``None``
        if no pending data available.
        """

    @overload
    def readinto(self, buf: AnyWritableBuf, maxlen: int, /) -> int | None:
        """
        Read bytes from the serial device and store them into ``buf``, which
        should be a buffer-like object.  At most ``len(buf)`` bytes are read.
        If ``maxlen`` is given and then at most ``min(maxlen, len(buf))`` bytes
        are read.

        Returns the number of bytes read and stored into ``buf`` or ``None``
        if no pending data available.
        """

    def readline(self) -> bytes:
        """
        Read a whole line from the serial device.

        Returns a bytes object containing the data, including the trailing
        newline character or ``None`` if no pending data available.
        """
        ...

    def readlines(self) -> List:
        """
        Read as much data as possible from the serial device, breaking it into
        lines.

        Returns a list of bytes objects, each object being one of the lines.
        Each line will include the newline character.
        """
        ...

    def write(self, buf: AnyReadableBuf, /) -> int:
        """
        Write the bytes from ``buf`` to the serial device.

        Returns the number of bytes written.
        """
        ...

    @overload
    def recv(self, data: int, /, *, timeout: int = 5000) -> bytes | None:
        """
        Receive data on the bus:

          - ``data`` can be an integer, which is the number of bytes to receive,
            or a mutable buffer, which will be filled with received bytes.
          - ``timeout`` is the timeout in milliseconds to wait for the receive.

        Return value: if ``data`` is an integer then a new buffer of the bytes received,
        otherwise the number of bytes read into ``data`` is returned.
        """

    @overload
    def recv(self, data: AnyWritableBuf, /, *, timeout: int = 5000) -> int | None:
        """
        Receive data on the bus:

          - ``data`` can be an integer, which is the number of bytes to receive,
            or a mutable buffer, which will be filled with received bytes.
          - ``timeout`` is the timeout in milliseconds to wait for the receive.

        Return value: if ``data`` is an integer then a new buffer of the bytes received,
        otherwise the number of bytes read into ``data`` is returned.
        """

    def send(self, buf: AnyWritableBuf | bytes | int, /, *, timeout: int = 5000) -> int:
        """
        Send data over the USB VCP:

          - ``data`` is the data to send (an integer to send, or a buffer object).
          - ``timeout`` is the timeout in milliseconds to wait for the send.

        Return value: number of bytes sent.
        """
        ...

    def irq(self, handler=None, trigger=IRQ_RX, hard=False) -> None:
        """
        Register *handler* to be called whenever an event specified by *trigger*
        occurs.  The *handler* function must take exactly one argument, which will
        be the USB VCP object.  Pass in ``None`` to disable the callback.

        Valid values for *trigger* are:

          - ``USB_VCP.IRQ_RX``: new data is available for reading from the USB VCP object.
        """
        ...
