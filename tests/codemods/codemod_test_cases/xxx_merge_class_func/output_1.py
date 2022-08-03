"""
network configuration. See: https://docs.micropython.org/en/v1.18/library/network.html

This module provides network drivers and routing configuration. To use this
module, a MicroPython variant/build with network capabilities must be installed.
Network drivers for specific hardware are available within this module and are
used to configure hardware network interface(s). Network services provided
by configured interfaces are then available for use via the :mod:`socket`
module.

For example::

    # connect/ show IP config a specific network interface
    # see below for examples of specific drivers
    import network
    import time
    nic = network.Driver(...)
    if not nic.isconnected():
        nic.connect()
        print("Waiting for connection...")
        while not nic.isconnected():
            time.sleep(1)
    print(nic.ifconfig())

    # now use socket as usual
    import socket
    addr = socket.getaddrinfo('micropython.org', 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(b'GET / HTTP/1.1\r\nHost: micropython.org\r\n\r\n')
    data = s.recv(1000)
    s.close()
"""
# MCU: {'ver': 'v1.18', 'port': 'esp32', 'arch': 'xtensawin', 'sysname': 'esp32', 'release': '1.18.0', 'name': 'micropython', 'mpy': 10757, 'version': '1.18.0', 'machine': 'ESP32 module (spiram) with ESP32', 'build': '', 'nodename': 'esp32', 'platform': 'esp32', 'family': 'micropython'}
# Stubber: 1.5.4
from typing import Callable, Coroutine, Dict, Generator, IO, Iterator, List, NoReturn, Optional, Tuple, Union, Any

AP_IF = 1  # type: int
AUTH_MAX = 8  # type: int
AUTH_OPEN = 0  # type: int
AUTH_WEP = 1  # type: int
AUTH_WPA2_ENTERPRISE = 5  # type: int
AUTH_WPA2_PSK = 3  # type: int
AUTH_WPA2_WPA3_PSK = 7  # type: int
AUTH_WPA3_PSK = 6  # type: int
AUTH_WPA_PSK = 2  # type: int
AUTH_WPA_WPA2_PSK = 4  # type: int
ETH_CONNECTED = 3  # type: int
ETH_DISCONNECTED = 4  # type: int
ETH_GOT_IP = 5  # type: int
ETH_INITIALIZED = 0  # type: int
ETH_STARTED = 1  # type: int
ETH_STOPPED = 2  # type: int


def LAN(*args, **kwargs) -> Any:
    ...


MODE_11B = 1  # type: int
MODE_11G = 2  # type: int
MODE_11N = 4  # type: int
PHY_DP83848 = 3  # type: int
PHY_IP101 = 1  # type: int
PHY_LAN8720 = 0  # type: int
PHY_RTL8201 = 2  # type: int


def PPP(*args, **kwargs) -> Any:
    ...


STAT_ASSOC_FAIL = 203  # type: int
STAT_BEACON_TIMEOUT = 200  # type: int
STAT_CONNECTING = 1001  # type: int
STAT_GOT_IP = 1010  # type: int
STAT_HANDSHAKE_TIMEOUT = 204  # type: int
STAT_IDLE = 1000  # type: int
STAT_NO_AP_FOUND = 201  # type: int
STAT_WRONG_PASSWORD = 202  # type: int
STA_IF = 0  # type: int


def WLAN(*args, **kwargs) -> Any:
    """
    Create a WLAN network interface object. Supported interfaces are
    ``network.STA_IF`` (station aka client, connects to upstream WiFi access
    points) and ``network.AP_IF`` (access point, allows other WiFi clients to
    connect). Availability of the methods below depends on interface type.
    For example, only STA interface may `WLAN.connect()` to an access point.
    """
    ...


def phy_mode(*args, **kwargs) -> Any:
    ...
