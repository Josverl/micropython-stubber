# .. module:: usocket
# origin: micropython\docs\library\usocket.rst
# v1.16
"""
   :synopsis: socket module

|see_cpython_module| :mod:`python:socket`.

This module provides access to the BSD socket interface.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: usocket
# .. function:: socket(af=AF_INET, type=SOCK_STREAM, proto=IPPROTO_TCP, /)
class socket:
    """
    Create a new socket using the given address family, socket type and
    protocol number. Note that specifying *proto* in most cases is not
    required (and not recommended, as some MicroPython ports may omit
    ``IPPROTO_*`` constants). Instead, *type* argument will select needed
    protocol automatically::

         # Create STREAM TCP socket
         socket(AF_INET, SOCK_STREAM)
         # Create DGRAM UDP socket
         socket(AF_INET, SOCK_DGRAM)
    """

    def __init__(self, af=AF_INET, type=SOCK_STREAM, proto=IPPROTO_TCP, /) -> None:
        ...

    # .. function:: inet_ntop(af, bin_addr)
    def inet_ntop(af, bin_addr) -> Any:
        """
        Convert a binary network address *bin_addr* of the given address family *af*
        to a textual representation::

             >>> usocket.inet_ntop(usocket.AF_INET, b"\x7f\0\0\1")
             '127.0.0.1'
        """
        ...

    # .. data:: AF_INET
    # .. data:: SOCK_STREAM
    # .. data:: IPPROTO_UDP
    # .. data:: usocket.SOL_*
    # .. data:: usocket.SO_*
    # .. data:: IPPROTO_SEC
    # .. method:: socket.close()
    def close(
        self,
    ) -> Any:
        """
        Mark the socket closed and release all resources. Once that happens, all future operations
        on the socket object will fail. The remote end will receive EOF indication if
        supported by protocol.

        Sockets are automatically closed when they are garbage-collected, but it is recommended
        to `close()` them explicitly as soon you finished working with them.
        """
        ...

    # .. method:: socket.listen([backlog])
    def listen(self, backlog: Optional[Any]) -> Any:
        """
        Enable a server to accept connections. If *backlog* is specified, it must be at least 0
        (if it's lower, it will be set to 0); and specifies the number of unaccepted connections
        that the system will allow before refusing new connections. If not specified, a default
        reasonable value is chosen.
        """
        ...

    # .. method:: socket.connect(address)
    def connect(self, address) -> Any:
        """
        Connect to a remote socket at *address*.
        """
        ...

    # .. method:: socket.sendall(bytes)
    def sendall(self, bytes) -> Any:
        """
        Send all data to the socket. The socket must be connected to a remote socket.
        Unlike `send()`, this method will try to send all of data, by sending data
        chunk by chunk consecutively.

        The behaviour of this method on non-blocking sockets is undefined. Due to this,
        on MicroPython, it's recommended to use `write()` method instead, which
        has the same "no short writes" policy for blocking sockets, and will return
        number of bytes sent on non-blocking sockets.
        """
        ...

    # .. method:: socket.sendto(bytes, address)
    def sendto(self, bytes, address) -> Any:
        """
        Send data to the socket. The socket should not be connected to a remote socket, since the
        destination socket is specified by *address*.
        """
        ...

    # .. method:: socket.setsockopt(level, optname, value)
    def setsockopt(self, level, optname, value) -> Any:
        """
        Set the value of the given socket option. The needed symbolic constants are defined in the
        socket module (SO_* etc.). The *value* can be an integer or a bytes-like object representing
        a buffer.
        """
        ...

    # .. method:: socket.setblocking(flag)
    def setblocking(self, flag) -> Any:
        """
        Set blocking or non-blocking mode of the socket: if flag is false, the socket is set to non-blocking,
        else to blocking mode.

        This method is a shorthand for certain `settimeout()` calls:

        * ``sock.setblocking(True)`` is equivalent to ``sock.settimeout(None)``
        * ``sock.setblocking(False)`` is equivalent to ``sock.settimeout(0)``
        """
        ...

    # .. method:: socket.read([size])
    def read(self, size: Optional[Any]) -> Any:
        """
        Read up to size bytes from the socket. Return a bytes object. If *size* is not given, it
        reads all data available from the socket until EOF; as such the method will not return until
        the socket is closed. This function tries to read as much data as
        requested (no "short reads"). This may be not possible with
        non-blocking socket though, and then less data will be returned.
        """
        ...

    # .. method:: socket.readline()
    def readline(
        self,
    ) -> Any:
        """
        Read a line, ending in a newline character.

        Return value: the line read.
        """
        ...


# .. exception:: usocket.error
