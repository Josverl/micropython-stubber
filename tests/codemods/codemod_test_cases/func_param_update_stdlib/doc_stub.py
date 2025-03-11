# fmt:off
"""
conditional function in stdlib stubs
"""
import socket
import sys

def wrap_socket(
    sock: socket.socket,
    *,
    server_side: bool = False,
    key: Incomplete = None,
    cert: Incomplete = None,
    cert_reqs: int = 0,
    cadata: bytes | None = None,
    server_hostname: str | None = None,
    do_handshake: bool = True,
) -> SSLSocket:
    """
    reference stub
    """
    ...