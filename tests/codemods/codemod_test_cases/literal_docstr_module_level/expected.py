# fmt: off
"""
MicroPython network module constants - documentation version

---
MicroPython network module constants
"""

# Network protocol constants
IPPROTO_UDP = 17
"""User Datagram Protocol"""
IPPROTO_TCP = 6
"""Transmission Control Protocol"""
IPPROTO_ICMP = 1
"""Internet Control Message Protocol"""

# Address family constants  
AF_INET = 2
"""IPv4 address family"""
AF_INET6 = 10
"""IPv6 address family"""

# Socket types
SOCK_STREAM = 1
"""Stream socket (TCP)"""
SOCK_DGRAM = 2
"""Datagram socket (UDP)"""

def connect():
    """Connect to a network endpoint"""
    ...

class Socket:
    def bind(self):
        """Bind socket to address"""
        ...