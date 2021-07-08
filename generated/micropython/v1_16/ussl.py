# .. module:: ussl
# origin: micropython\docs\library\ussl.rst
# v1.16
"""
   :synopsis: TLS/SSL wrapper for socket objects

|see_cpython_module| :mod:`python:ssl`.

This module provides access to Transport Layer Security (previously and
widely known as “Secure Sockets Layer”) encryption and peer authentication
facilities for network sockets, both client-side and server-side.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: ussl
# .. function:: ussl.wrap_socket(sock, server_side=False, keyfile=None, certfile=None, cert_reqs=CERT_NONE, ca_certs=None, do_handshake=True)
def wrap_socket(
    sock,
    server_side=False,
    keyfile=None,
    certfile=None,
    cert_reqs=None,
    ca_certs=None,
    do_handshake=True,
) -> Any:
    """
     Takes a `stream` *sock* (usually usocket.socket instance of ``SOCK_STREAM`` type),
     and returns an instance of ssl.SSLSocket, which wraps the underlying stream in
     an SSL context. Returned object has the usual `stream` interface methods like
     ``read()``, ``write()``, etc.
     A server-side SSL socket should be created from a normal socket returned from
     :meth:`~usocket.socket.accept()` on a non-SSL listening server socket.

     - *do_handshake* determines whether the handshake is done as part of the ``wrap_socket``
       or whether it is deferred to be done as part of the initial reads or writes
       (there is no ``do_handshake`` method as in CPython).
       For blocking sockets doing the handshake immediately is standard. For non-blocking
       sockets (i.e. when the *sock* passed into ``wrap_socket`` is in non-blocking mode)
       the handshake should generally be deferred because otherwise ``wrap_socket`` blocks
       until it completes. Note that in AXTLS the handshake can be deferred until the first
       read or write but it then blocks until completion.

     Depending on the underlying module implementation in a particular
     :term:`MicroPython port`, some or all keyword arguments above may be not supported.
    """
    ...


# .. data:: ssl.SSLError
# .. data:: ussl.CERT_NONE
