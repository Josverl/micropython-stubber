# fmt: off
"""
MicroPython network constants - doc version with literal docstrings
"""

# Protocol constants (doc stub with rich docstrings)
IPPROTO_UDP = 17
"""User Datagram Protocol. Used for connectionless, unreliable transmission."""
IPPROTO_TCP = 6
"""Transmission Control Protocol. Used for reliable, connection-oriented transmission."""

# Address family constants
AF_INET = 2
"""IPv4 address family. Standard Internet Protocol version 4."""
AF_INET6 = 10
"""IPv6 address family. Internet Protocol version 6 with extended addressing."""

# Socket type constants
SOCK_STREAM = 1
"""Stream socket type. Provides reliable, ordered, connection-based data transmission (TCP)."""
SOCK_DGRAM = 2
"""Datagram socket type. Provides connectionless, unreliable transmission (UDP)."""

# Socket option constants
SOL_SOCKET = 1
"""Socket-level options. Used with setsockopt/getsockopt for socket-level configuration."""
SO_REUSEADDR = 2
"""Allow reuse of local addresses. Useful for server applications that need to restart."""

def example_function():
    """Example function with documentation"""
    ...

class ExampleClass:
    """Example class with documentation"""
    
    def method(self):
        """Example method with documentation"""
        ...