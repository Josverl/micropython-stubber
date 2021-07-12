from typing import Any, Optional, Union, Tuple

# .. module:: usocket
# origin: micropython\docs\library\usocket.rst
# v1.16
"""
   :synopsis: socket module

|see_cpython_module| :mod:`python:socket`.

This module provides access to the BSD socket interface.
"""
# .. admonition:: Difference to CPython
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


# .. function:: getaddrinfo(host, port, af=0, type=0, proto=0, flags=0, /)
def getaddrinfo(host, port, af=0, type=0, proto=0, flags=0, /) -> Any:
    """
    Translate the host/port argument into a sequence of 5-tuples that contain all the
    necessary arguments for creating a socket connected to that service. Arguments
    *af*, *type*, and *proto* (which have the same meaning as for the `socket()` function)
    can be used to filter which kind of addresses are returned. If a parameter is not
    specified or zero, all combinations of addresses can be returned (requiring
    filtering on the user side).

    The resulting list of 5-tuples has the following structure::

       (family, type, proto, canonname, sockaddr)

    The following example shows how to connect to a given url::

       s = usocket.socket()
       # This assumes that if "type" is not specified, an address for
       # SOCK_STREAM will be returned, which may be not true
       s.connect(usocket.getaddrinfo('www.micropython.org', 80)[0][-1])

    Recommended use of filtering params::

       s = usocket.socket()
       # Guaranteed to return an address which can be connect'ed to for
       # stream operation.
       s.connect(usocket.getaddrinfo('www.micropython.org', 80, 0, SOCK_STREAM)[0][-1])
    """
    ...


#    .. admonition:: Difference to CPython
# .. function:: inet_ntop(af, bin_addr)
def inet_ntop(af, bin_addr) -> Any:
    """
    Convert a binary network address *bin_addr* of the given address family *af*
    to a textual representation::

         >>> usocket.inet_ntop(usocket.AF_INET, b"\x7f\0\0\1")
         '127.0.0.1'
    """
    ...


# .. function:: inet_pton(af, txt_addr)
def inet_pton(af, txt_addr) -> Any:
    """
    Convert a textual network address *txt_addr* of the given address family *af*
    to a binary representation::

         >>> usocket.inet_pton(usocket.AF_INET, "1.2.3.4")
         b'\x01\x02\x03\x04'
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


# .. method:: socket.bind(address)
def bind(self, address) -> Any:
    """
    Bind the socket to *address*. The socket must not already be bound.
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


# .. method:: socket.accept()
def accept(
    self,
) -> Any:
    """
    Accept a connection. The socket must be bound to an address and listening for connections.
    The return value is a pair (conn, address) where conn is a new socket object usable to send
    and receive data on the connection, and address is the address bound to the socket on the
    other end of the connection.
    """
    ...


# .. method:: socket.connect(address)
def connect(self, address) -> Any:
    """
    Connect to a remote socket at *address*.
    """
    ...


# .. method:: socket.send(bytes)
def send(self, bytes) -> Any:
    """
    Send data to the socket. The socket must be connected to a remote socket.
    Returns number of bytes sent, which may be smaller than the length of data
    ("short write").
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


# .. method:: socket.recv(bufsize)
def recv(self, bufsize) -> Any:
    """
    Receive data from the socket. The return value is a bytes object representing the data
    received. The maximum amount of data to be received at once is specified by bufsize.
    """
    ...


# .. method:: socket.sendto(bytes, address)
def sendto(self, bytes, address) -> Any:
    """
    Send data to the socket. The socket should not be connected to a remote socket, since the
    destination socket is specified by *address*.
    """
    ...


# .. method:: socket.recvfrom(bufsize)
def recvfrom(self, bufsize) -> Any:
    """
    Receive data from the socket. The return value is a pair *(bytes, address)* where *bytes* is a
    bytes object representing the data received and *address* is the address of the socket sending
    the data.
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


# .. method:: socket.settimeout(value)
def settimeout(self, value) -> Any:
    """
    **Note**: Not every port supports this method, see below.

    Set a timeout on blocking socket operations. The value argument can be a nonnegative floating
    point number expressing seconds, or None. If a non-zero value is given, subsequent socket operations
    will raise an `OSError` exception if the timeout period value has elapsed before the operation has
    completed. If zero is given, the socket is put in non-blocking mode. If None is given, the socket
    is put in blocking mode.

    Not every :term:`MicroPython port` supports this method. A more portable and
    generic solution is to use `uselect.poll` object. This allows to wait on
    multiple objects at the same time (and not just on sockets, but on generic
    `stream` objects which support polling). Example::

         # Instead of:
         s.settimeout(1.0)  # time in seconds
         s.read(10)  # may timeout

         # Use:
         poller = uselect.poll()
         poller.register(s, uselect.POLLIN)
         res = poller.poll(1000)  # time in milliseconds
         if not res:
             # s is still not ready for input, i.e. operation timed out
    """
    ...


#    .. admonition:: Difference to CPython
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


# .. method:: socket.makefile(mode='rb', buffering=0, /)
def makefile(self, mode="rb", buffering=0, /) -> Any:
    """
    Return a file object associated with the socket. The exact returned type depends on the arguments
    given to makefile(). The support is limited to binary modes only ('rb', 'wb', and 'rwb').
    CPython's arguments: *encoding*, *errors* and *newline* are not supported.
    """
    ...


#    .. admonition:: Difference to CPython
#    .. admonition:: Difference to CPython
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


# .. method:: socket.readinto(buf[, nbytes])
def readinto(self, buf, nbytes: Optional[Any]) -> Any:
    """
    Read bytes into the *buf*.  If *nbytes* is specified then read at most
    that many bytes.  Otherwise, read at most *len(buf)* bytes. Just as
    `read()`, this method follows "no short reads" policy.

    Return value: number of bytes read and stored into *buf*.
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


# .. method:: socket.write(buf)
def write(self, buf) -> Any:
    """
    Write the buffer of bytes to the socket. This function will try to
    write all data to a socket (no "short writes"). This may be not possible
    with a non-blocking socket though, and returned value will be less than
    the length of *buf*.

    Return value: number of bytes written.
    """
    ...


# .. exception:: usocket.error
#    .. admonition:: Difference to CPython
