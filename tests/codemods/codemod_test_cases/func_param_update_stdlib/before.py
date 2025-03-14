# fmt:off
"""
conditional function in stdlib stubs
"""
import socket
import sys

if sys.version_info < (3, 12):
    def wrap_socket(
        sock: socket.socket,
        keyfile: StrOrBytesPath | None = None,
        certfile: StrOrBytesPath | None = None,
        server_side: bool = False,
        cert_reqs: int = ...,
        ssl_version: int = ...,
        ca_certs: str | None = None,
        do_handshake_on_connect: bool = True,
        suppress_ragged_eofs: bool = True,
        ciphers: str | None = None,
    ) -> SSLSocket:
        """
        stdlib docs
        """
        ...
