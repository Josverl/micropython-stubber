"""
ESP-NOW :doc:`asyncio` support.

MicroPython module: https://docs.micropython.org/en/v1.24.0/library/aioespnow.html
"""

# source version: v1.24.1
# origin module:: repos/micropython/docs/library/espnow.rst
# source version: v1.24.1
# origin module:: repos/micropython/docs/library/espnow.rst
from __future__ import annotations

from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

from _espnow import ESPNowBase  # type: ignore
from _typeshed import Incomplete, TypeAlias
from typing_extensions import TypeAlias

_MACAddress: TypeAlias = bytes
_PeerInfo: TypeAlias = Tuple[_MACAddress, bytes, int, int, bool]

MAX_DATA_LEN: Incomplete = 250
KEY_LEN: Incomplete = 16
ADDR_LEN: Incomplete = 6
MAX_TOTAL_PEER_NUM: Incomplete = 20
MAX_ENCRYPT_PEER_NUM: Incomplete = 6

class ESPNow(ESPNowBase, Iterator):
    """
    Returns the singleton ESPNow object. As this is a singleton, all calls to
    `espnow.ESPNow()` return a reference to the same object.

    .. note::
      Some methods are available only on the ESP32 due to code size
      restrictions on the ESP8266 and differences in the Espressif API.
    """

    peers_table: Dict
    """\
    A reference to the **peer device table**: a dict of known peer devices
    and rssi values::
    
    {peer: [rssi, time_ms], ...}
    
    where:
    
    - ``peer`` is the peer MAC address (as `bytes`);
    - ``rssi`` is the wifi signal strength in dBm (-127 to 0) of the last
    message received from the peer; and
    - ``time_ms`` is the time the message was received (in milliseconds since
    system boot - wraps every 12 days).
    
    Example::
    
    >>> e.peers_table
    {b'\xaa\xaa\xaa\xaa\xaa\xaa': [-31, 18372],
    b'\xbb\xbb\xbb\xbb\xbb\xbb': [-43, 12541]}
    
    **Note**: the ``mac`` addresses returned by `recv()` are references to
    the ``peer`` key values in the **peer device table**.
    
    **Note**: RSSI and timestamp values in the device table are updated only
    when the message is read by the application.
    """
    def __init__(self) -> None: ...
    def active(self, flag: Optional[Any] = None) -> Incomplete:
        """
        Initialise or de-initialise the ESP-NOW communication protocol depending on
        the value of the ``flag`` optional argument.

        Arguments:

          - *flag*: Any python value which can be converted to a boolean type.

            - ``True``: Prepare the software and hardware for use of the ESP-NOW
              communication protocol, including:

              - initialise the ESPNow data structures,
              - allocate the recv data buffer,
              - invoke esp_now_init() and
              - register the send and recv callbacks.

            - ``False``: De-initialise the Espressif ESP-NOW software stack
              (esp_now_deinit()), disable callbacks, deallocate the recv
              data buffer and deregister all peers.

        If *flag* is not provided, return the current status of the ESPNow
        interface.

        Returns:

            ``True`` if interface is currently *active*, else ``False``.
        """
        ...

    def config(self, param) -> str:
        """
        Set or get configuration values of the ESPNow interface. To set values, use
        the keyword syntax, and one or more parameters can be set at a time. To get
        a value the parameter name should be quoted as a string, and just one
        parameter is queried at a time.

        **Note:** *Getting* parameters is not supported on the ESP8266.

        Options:

            *rxbuf*: (default=526) Get/set the size in bytes of the internal
            buffer used to store incoming ESPNow packet data. The default size is
            selected to fit two max-sized ESPNow packets (250 bytes) with associated
            mac_address (6 bytes), a message byte count (1 byte) and RSSI data plus
            buffer overhead. Increase this if you expect to receive a lot of large
            packets or expect bursty incoming traffic.

            **Note:** The recv buffer is allocated by `ESPNow.active()`. Changing
            this value will have no effect until the next call of
            `ESPNow.active(True)<ESPNow.active()>`.

            *timeout_ms*: (default=300,000) Default timeout (in milliseconds)
            for receiving ESPNow messages. If *timeout_ms* is less than zero, then
            wait forever. The timeout can also be provided as arg to
            `recv()`/`irecv()`/`recvinto()`.

            *rate*: (ESP32 only, IDF>=4.3.0 only) Set the transmission speed for
            ESPNow packets. Must be set to a number from the allowed numeric values
            in `enum wifi_phy_rate_t
            <https://docs.espressif.com/projects/esp-idf/en/v4.4.1/esp32/
            api-reference/network/esp_wifi.html#_CPPv415wifi_phy_rate_t>`_.

        Returns:

            ``None`` or the value of the parameter being queried.

        Raises:

            - ``OSError(num, "ESP_ERR_ESPNOW_NOT_INIT")`` if not initialised.
            - ``ValueError()`` on invalid configuration options or values.
        """
        ...

    def send(self, peer, msg, mac: _MACAddress | None = None, sync=True) -> Incomplete:
        """
        Send the data contained in ``msg`` to the peer with given network ``mac``
        address. In the second form, ``mac=None`` and ``sync=True``. The peer must
        be registered with `ESPNow.add_peer()<ESPNow.add_peer()>` before the
        message can be sent.

        Arguments:

          - *mac*: byte string exactly ``espnow.ADDR_LEN`` (6 bytes) long or
            ``None``. If *mac* is ``None`` (ESP32 only) the message will be sent
            to all registered peers, except any broadcast or multicast MAC
            addresses.

          - *msg*: string or byte-string up to ``espnow.MAX_DATA_LEN`` (250)
            bytes long.

          - *sync*:

            - ``True``: (default) send ``msg`` to the peer(s) and wait for a
              response (or not).

            - ``False`` send ``msg`` and return immediately. Responses from the
              peers will be discarded.

        Returns:

          ``True`` if ``sync=False`` or if ``sync=True`` and *all* peers respond,
          else ``False``.

        Raises:

          - ``OSError(num, "ESP_ERR_ESPNOW_NOT_INIT")`` if not initialised.
          - ``OSError(num, "ESP_ERR_ESPNOW_NOT_FOUND")`` if peer is not registered.
          - ``OSError(num, "ESP_ERR_ESPNOW_IF")`` the wifi interface is not
            `active()<network.WLAN.active>`.
          - ``OSError(num, "ESP_ERR_ESPNOW_NO_MEM")`` internal ESP-NOW buffers are
            full.
          - ``ValueError()`` on invalid values for the parameters.

        **Note**: A peer will respond with success if its wifi interface is
        `active()<network.WLAN.active>` and set to the same channel as the sender,
        regardless of whether it has initialised it's ESP-NOW system or is
        actively listening for ESP-NOW traffic (see the Espressif ESP-NOW docs).
        """
        ...

    def recv(self, timeout_ms: Optional[Any] = None) -> Union[List, Tuple[None, None]]:
        """
        Wait for an incoming message and return the ``mac`` address of the peer and
        the message. **Note**: It is **not** necessary to register a peer (using
        `add_peer()<ESPNow.add_peer()>`) to receive a message from that peer.

        Arguments:

            - *timeout_ms*: (Optional): May have the following values.

              - ``0``: No timeout. Return immediately if no data is available;
              - ``> 0``: Specify a timeout value in milliseconds;
              - ``< 0``: Do not timeout, ie. wait forever for new messages; or
              - ``None`` (or not provided): Use the default timeout value set with
                `ESPNow.config()`.

        Returns:

          - ``(None, None)`` if timeout is reached before a message is received, or

          - ``[mac, msg]``: where:

            - ``mac`` is a bytestring containing the address of the device which
              sent the message, and
            - ``msg`` is a bytestring containing the message.

        Raises:

          - ``OSError(num, "ESP_ERR_ESPNOW_NOT_INIT")`` if not initialised.
          - ``OSError(num, "ESP_ERR_ESPNOW_IF")`` if the wifi interface is not
            `active()<network.WLAN.active>`.
          - ``ValueError()`` on invalid *timeout_ms* values.

        `ESPNow.recv()` will allocate new storage for the returned list and the
        ``peer`` and ``msg`` bytestrings. This can lead to memory fragmentation if
        the data rate is high. See `ESPNow.irecv()` for a memory-friendly
        alternative.
        """
        ...

    def irecv(self, timeout_ms: Optional[int] = None) -> Tuple[_MACAddress | bytearray | None, bytearray | None]:
        """
        Works like `ESPNow.recv()` but will reuse internal bytearrays to store the
        return values: ``[mac, msg]``, so that no new memory is allocated on each
        call.

        Arguments:

            *timeout_ms*: (Optional) Timeout in milliseconds (see `ESPNow.recv()`).

        Returns:

          - As for `ESPNow.recv()`, except that ``msg`` is a bytearray, instead of
            a bytestring. On the ESP8266, ``mac`` will also be a bytearray.

        Raises:

          - See `ESPNow.recv()`.

        **Note:** You may also read messages by iterating over the ESPNow object,
        which will use the `irecv()` method for alloc-free reads, eg: ::

          import espnow
          e = espnow.ESPNow(); e.active(True)
          for mac, msg in e:
              print(mac, msg)
              if mac is None:   # mac, msg will equal (None, None) on timeout
                  break
        """
        ...

    def recvinto(self, data: List, timeout_ms: Optional[int] = None) -> int:
        """
        Wait for an incoming message and return the length of the message in bytes.
        This is the low-level method used by both `recv()<ESPNow.recv()>` and
        `irecv()` to read messages.

        Arguments:

            *data*: A list of at least two elements, ``[peer, msg]``. ``msg`` must
            be a bytearray large enough to hold the message (250 bytes). On the
            ESP8266, ``peer`` should be a bytearray of 6 bytes. The MAC address of
            the sender and the message will be stored in these bytearrays (see Note
            on ESP32 below).

            *timeout_ms*: (Optional) Timeout in milliseconds (see `ESPNow.recv()`).

        Returns:

          - Length of message in bytes or 0 if *timeout_ms* is reached before a
            message is received.

        Raises:

          - See `ESPNow.recv()`.

        **Note:** On the ESP32:

        - It is unnecessary to provide a bytearray in the first element of the
          ``data`` list because it will be replaced by a reference to a unique
          ``peer`` address in the **peer device table** (see `ESPNow.peers_table`).
        - If the list is at least 4 elements long, the rssi and timestamp values
          will be saved as the 3rd and 4th elements.
        """
        ...

    def any(self) -> bool:
        """
        Check if data is available to be read with `ESPNow.recv()`.

        For more sophisticated querying of available characters use `select.poll()`::

          import select
          import espnow

          e = espnow.ESPNow()
          poll = select.poll()
          poll.register(e, select.POLLIN)
          poll.poll(timeout)

        Returns:

           ``True`` if data is available to be read, else ``False``.
        """
        ...

    def stats(self) -> Tuple[int, int, int, int, int]:
        """
        Returns:

          A 5-tuple containing the number of packets sent/received/lost:

          ``(tx_pkts, tx_responses, tx_failures, rx_packets, rx_dropped_packets)``

        Incoming packets are *dropped* when the recv buffers are full. To reduce
        packet loss, increase the ``rxbuf`` config parameters and ensure you are
        reading messages as quickly as possible.

        **Note**: Dropped packets will still be acknowledged to the sender as
        received.
        """
        ...

    def set_pmk(self, pmk: bytes | bytearray | str) -> None:
        """
        Set the Primary Master Key (PMK) which is used to encrypt the Local Master
        Keys (LMK) for encrypting messages. If this is not set, a default PMK is
        used by the underlying Espressif ESP-NOW software stack.

        **Note:** messages will only be encrypted if *lmk* is also set in
        `ESPNow.add_peer()` (see `Security
        <https://docs.espressif.com/projects/esp-idf/en/latest/
        esp32/api-reference/network/esp_now.html#security>`_ in the Espressif API
        docs).

        Arguments:

          *pmk*: Must be a byte string, bytearray or string of length
          `espnow.KEY_LEN` (16 bytes).

        Returns:

          ``None``

        Raises:

          ``ValueError()`` on invalid *pmk* values.
        """
        ...

    def add_peer(
        self,
        mac: _MACAddress,
        lmk: Optional[bytes | bytearray | str] = None,
        channel: Optional[int] = None,
        ifidx: Optional[int] = None,
        encrypt: Optional[bool] = True,
    ) -> Incomplete:
        """
        Add/register the provided *mac* address as a peer. Additional parameters may
        also be specified as positional or keyword arguments (any parameter set to
        ``None`` will be set to it's default value):

        Arguments:

            - *mac*: The MAC address of the peer (as a 6-byte byte-string).

            - *lmk*: The Local Master Key (LMK) key used to encrypt data
              transfers with this peer (unless the *encrypt* parameter is set to
              ``False``). Must be:

              - a byte-string or bytearray or string of length ``espnow.KEY_LEN``
                (16 bytes), or

              - any non ``True`` python value (default= ``b''``), signifying an
                *empty* key which will disable encryption.

            - *channel*: The wifi channel (2.4GHz) to communicate with this peer.
              Must be an integer from 0 to 14. If channel is set to 0 the current
              channel of the wifi device will be used. (default=0)

            - *ifidx*: (ESP32 only) Index of the wifi interface which will be
              used to send data to this peer. Must be an integer set to
              ``network.STA_IF`` (=0) or ``network.AP_IF`` (=1).
              (default=0/``network.STA_IF``). See `ESPNow and Wifi Operation`_
              below for more information.

            - *encrypt*: (ESP32 only) If set to ``True`` data exchanged with
              this peer will be encrypted with the PMK and LMK. (default =
              ``True`` if *lmk* is set to a valid key, else ``False``)

            **ESP8266**: Keyword args may not be used on the ESP8266.

            **Note:** The maximum number of peers which may be registered is 20
            (`espnow.MAX_TOTAL_PEER_NUM`), with a maximum of 6
            (`espnow.MAX_ENCRYPT_PEER_NUM`) of those peers with encryption enabled
            (see `ESP_NOW_MAX_ENCRYPT_PEER_NUM <https://docs.espressif.com/
            projects/esp-idf/en/latest/esp32/api-reference/network/
            esp_now.html#c.ESP_NOW_MAX_ENCRYPT_PEER_NUM>`_ in the Espressif API
            docs).

        Raises:

            - ``OSError(num, "ESP_ERR_ESPNOW_NOT_INIT")`` if not initialised.
            - ``OSError(num, "ESP_ERR_ESPNOW_EXIST")`` if *mac* is already
              registered.
            - ``OSError(num, "ESP_ERR_ESPNOW_FULL")`` if too many peers are
              already registered.
            - ``ValueError()`` on invalid keyword args or values.
        """
        ...

    def del_peer(self, mac: _MACAddress) -> None:
        """
        Deregister the peer associated with the provided *mac* address.

        Returns:

            ``None``

        Raises:

            - ``OSError(num, "ESP_ERR_ESPNOW_NOT_INIT")`` if not initialised.
            - ``OSError(num, "ESP_ERR_ESPNOW_NOT_FOUND")`` if *mac* is not
              registered.
            - ``ValueError()`` on invalid *mac* values.
        """
        ...

    def get_peer(self, mac: _MACAddress) -> _PeerInfo:
        """
        Return information on a registered peer.

        Returns:

            ``(mac, lmk, channel, ifidx, encrypt)``: a tuple of the "peer
            info" associated with the given *mac* address.

        Raises:

            - ``OSError(num, "ESP_ERR_ESPNOW_NOT_INIT")`` if not initialised.
            - ``OSError(num, "ESP_ERR_ESPNOW_NOT_FOUND")`` if *mac* is not
              registered.
            - ``ValueError()`` on invalid *mac* values.
        """
        ...

    def peer_count(self) -> int:
        """
        Return the number of registered peers:

        - ``(peer_num, encrypt_num)``: where

          - ``peer_num`` is the number of peers which are registered, and
          - ``encrypt_num`` is the number of encrypted peers.
        """
        ...

    def get_peers(self) -> Tuple:
        """
        Return the "peer info" parameters for all the registered peers (as a tuple
        of tuples).
        """
        ...

    def mod_peer(
        self,
        mac: _MACAddress,
        lmk: Optional[bytes | bytearray | str] = None,
        channel: Optional[int] = None,
        ifidx: Optional[int] = None,
        encrypt: Optional[bool] = True,
    ) -> None:
        """
        Modify the parameters of the peer associated with the provided *mac*
        address. Parameters may be provided as positional or keyword arguments
        (see `ESPNow.add_peer()`). Any parameter that is not set (or set to
        ``None``) will retain the existing value for that parameter.
        """
        ...

    def irq(self, callback: Callable) -> Incomplete:
        """
        Set a callback function to be called *as soon as possible* after a message has
        been received from another ESPNow device. The callback function will be called
        with the `ESPNow` instance object as an argument. For more reliable operation,
        it is recommended to read out as many messages as are available when the
        callback is invoked and to set the read timeout to zero, eg: ::

              def recv_cb(e):
                  while True:  # Read out all messages waiting in the buffer
                      mac, msg = e.irecv(0)  # Don't wait if no messages left
                      if mac is None:
                          return
                      print(mac, msg)
              e.irq(recv_cb)

        The `irq()<ESPNow.irq()>` callback method is an alternative method for
        processing incoming messages, especially if the data rate is moderate
        and the device is *not too busy* but there are some caveats:

        - The scheduler stack *can* overflow and callbacks will be missed if
          packets are arriving at a sufficient rate or if other MicroPython components
          (eg, bluetooth, machine.Pin.irq(), machine.timer, i2s, ...) are exercising
          the scheduler stack. This method may be less reliable for dealing with
          bursts of messages, or high throughput or on a device which is busy dealing
          with other hardware operations.

        - For more information on *scheduled* function callbacks see:
          `micropython.schedule()<micropython.schedule>`.
        """
        ...

class AIOESPNow(ESPNow):
    """
    The `AIOESPNow` class inherits all the methods of `ESPNow<espnow.ESPNow>`
    and extends the interface with the following async methods.
    """

    def __init__(self) -> None: ...
    async def arecv(self) -> Incomplete:
        """
        Asyncio support for `ESPNow.recv()`. Note that this method does not take a
        timeout value as argument.
        """
        ...

    async def airecv(self) -> Incomplete:
        """
        Asyncio support for `ESPNow.irecv()`. Note that this method does not take a
        timeout value as argument.
        """
        ...

    async def asend(self, msg) -> Incomplete:
        """
        Asyncio support for `ESPNow.send()`.
        """
        ...

    def _aiter__(self) -> Incomplete:
        """
        `AIOESPNow` also supports reading incoming messages by asynchronous
        iteration using ``async for``; eg::

          e = AIOESPNow()
          e.active(True)
          async def recv_till_halt(e):
              async for mac, msg in e:
                  print(mac, msg)
                  if msg == b'halt':
                    break
          asyncio.run(recv_till_halt(e))
        """
        ...

    async def __anext__(self) -> Incomplete:
        """
        `AIOESPNow` also supports reading incoming messages by asynchronous
        iteration using ``async for``; eg::

          e = AIOESPNow()
          e.active(True)
          async def recv_till_halt(e):
              async for mac, msg in e:
                  print(mac, msg)
                  if msg == b'halt':
                    break
          asyncio.run(recv_till_halt(e))
        """
        ...
