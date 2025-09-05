# fmt: off
"""
MicroPython network module constants
"""

# Network protocol constants
IPPROTO_UDP = 17
IPPROTO_TCP = 6
IPPROTO_ICMP = 1

# Address family constants  
AF_INET = 2
AF_INET6 = 10

# Socket types
SOCK_STREAM = 1
SOCK_DGRAM = 2

def connect(): ...

class Socket:
    def bind(self): ...