# .. module:: ubluetooth
# origin: micropython\docs\library\ubluetooth.rst
# v1.16
"""
   :synopsis: Low-level Bluetooth radio functionality

This module provides an interface to a Bluetooth controller on a board.
Currently this supports Bluetooth Low Energy (BLE) in Central, Peripheral,
Broadcaster, and Observer roles, as well as GATT Server and Client and L2CAP
connection-oriented-channels. A device may operate in multiple roles
concurrently. Pairing (and bonding) is supported on some ports.

This API is intended to match the low-level Bluetooth protocol and provide
building-blocks for higher-level abstractions such as specific device types.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: ubluetooth
# .. class:: BLE()
# .. class:: BLE()

# class:: BLE
class BLE:
    """
    Returns the singleton BLE object.
    """

    def __init__(
        self,
    ) -> None:
        ...

    # .. method:: BLE.active([active], /)
    def active(self, active: Optional[Any], /) -> Any:
        """
        Optionally changes the active state of the BLE radio, and returns the
        current state.

        The radio must be made active before using any other methods on this class.
        """
        ...

    # .. method:: BLE.irq(handler, /)
    def irq(self, handler, /) -> Any:
        """
            Registers a callback for events from the BLE stack. The *handler* takes two
            arguments, ``event`` (which will be one of the codes below) and ``data``
            (which is an event-specific tuple of values).

            **Note:** As an optimisation to prevent unnecessary allocations, the ``addr``,
            ``adv_data``, ``char_data``, ``notify_data``, and ``uuid`` entries in the
            tuples are read-only memoryview instances pointing to ubluetooth's internal
            ringbuffer, and are only valid during the invocation of the IRQ handler
            function.  If your program needs to save one of these values to access after
            the IRQ handler has returned (e.g. by saving it in a class instance or global
            variable), then it needs to take a copy of the data, either by using ``bytes()``
            or ``bluetooth.UUID()``, like this::

                connected_addr = bytes(addr)  # equivalently: adv_data, char_data, or notify_data
                matched_uuid = bluetooth.UUID(uuid)

            For example, the IRQ handler for a scan result might inspect the ``adv_data``
            to decide if it's the correct device, and only then copy the address data to be
            used elsewhere in the program.  And to print data from within the IRQ handler,
            ``print(bytes(addr))`` will be needed.

            An event handler showing all possible events::

                def bt_irq(event, data):
                    if event == _IRQ_CENTRAL_CONNECT:
                        # A central has connected to this peripheral.
                        conn_handle, addr_type, addr = data
                    elif event == _IRQ_CENTRAL_DISCONNECT:
                        # A central has disconnected from this peripheral.
                        conn_handle, addr_type, addr = data
                    elif event == _IRQ_GATTS_WRITE:
                        # A client has written to this characteristic or descriptor.
                        conn_handle, attr_handle = data
                    elif event == _IRQ_GATTS_READ_REQUEST:
                        # A client has issued a read. Note: this is only supported on STM32.
                        # Return a non-zero integer to deny the read (see below), or zero (or None)
                        # to accept the read.
                        conn_handle, attr_handle = data
                    elif event == _IRQ_SCAN_RESULT:
                        # A single scan result.
                        addr_type, addr, adv_type, rssi, adv_data = data
                    elif event == _IRQ_SCAN_DONE:
                        # Scan duration finished or manually stopped.
                        pass
                    elif event == _IRQ_PERIPHERAL_CONNECT:
                        # A successful gap_connect().
                        conn_handle, addr_type, addr = data
                    elif event == _IRQ_PERIPHERAL_DISCONNECT:
                        # Connected peripheral has disconnected.
                        conn_handle, addr_type, addr = data
                    elif event == _IRQ_GATTC_SERVICE_RESULT:
                        # Called for each service found by gattc_discover_services().
                        conn_handle, start_handle, end_handle, uuid = data
                    elif event == _IRQ_GATTC_SERVICE_DONE:
                        # Called once service discovery is complete.
                        # Note: Status will be zero on success, implementation-specific value otherwise.
                        conn_handle, status = data
                    elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
                        # Called for each characteristic found by gattc_discover_services().
                        conn_handle, def_handle, value_handle, properties, uuid = data
                    elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
                        # Called once service discovery is complete.
                        # Note: Status will be zero on success, implementation-specific value otherwise.
                        conn_handle, status = data
                    elif event == _IRQ_GATTC_DESCRIPTOR_RESULT:
                        # Called for each descriptor found by gattc_discover_descriptors().
                        conn_handle, dsc_handle, uuid = data
                    elif event == _IRQ_GATTC_DESCRIPTOR_DONE:
                        # Called once service discovery is complete.
                        # Note: Status will be zero on success, implementation-specific value otherwise.
                        conn_handle, status = data
                    elif event == _IRQ_GATTC_READ_RESULT:
                        # A gattc_read() has completed.
                        conn_handle, value_handle, char_data = data
                    elif event == _IRQ_GATTC_READ_DONE:
                        # A gattc_read() has completed.
                        # Note: The value_handle will be zero on btstack (but present on NimBLE).
                        # Note: Status will be zero on success, implementation-specific value otherwise.
                        conn_handle, value_handle, status = data
                    elif event == _IRQ_GATTC_WRITE_DONE:
                        # A gattc_write() has completed.
                        # Note: The value_handle will be zero on btstack (but present on NimBLE).
                        # Note: Status will be zero on success, implementation-specific value otherwise.
                        conn_handle, value_handle, status = data
                    elif event == _IRQ_GATTC_NOTIFY:
                        # A server has sent a notify request.
                        conn_handle, value_handle, notify_data = data
                    elif event == _IRQ_GATTC_INDICATE:
                        # A server has sent an indicate request.
                        conn_handle, value_handle, notify_data = data
                    elif event == _IRQ_GATTS_INDICATE_DONE:
                        # A client has acknowledged the indication.
                        # Note: Status will be zero on successful acknowledgment, implementation-specific value otherwise.
                        conn_handle, value_handle, status = data
                    elif event == _IRQ_MTU_EXCHANGED:
                        # ATT MTU exchange complete (either initiated by us or the remote device).
                        conn_handle, mtu = data
                    elif event == _IRQ_L2CAP_ACCEPT:
                        # A new channel has been accepted.
                        # Return a non-zero integer to reject the connection, or zero (or None) to accept.
                        conn_handle, cid, psm, our_mtu, peer_mtu = data
                    elif event == _IRQ_L2CAP_CONNECT:
                        # A new channel is now connected (either as a result of connecting or accepting).
                        conn_handle, cid, psm, our_mtu, peer_mtu = data
                    elif event == _IRQ_L2CAP_DISCONNECT:
                        # Existing channel has disconnected (status is zero), or a connection attempt failed (non-zero status).
                        conn_handle, cid, psm, status = data
                    elif event == _IRQ_L2CAP_RECV:
                        # New data is available on the channel. Use l2cap_recvinto to read.
                        conn_handle, cid = data
                    elif event == _IRQ_L2CAP_SEND_READY:
                        # A previous l2cap_send that returned False has now completed and the channel is ready to send again.
                        # If status is non-zero, then the transmit buffer overflowed and the application should re-send the data.
                        conn_handle, cid, status = data
                    elif event == _IRQ_CONNECTION_UPDATE:
                        # The remote device has updated connection parameters.
                        conn_handle, conn_interval, conn_latency, supervision_timeout, status = data
                    elif event == _IRQ_ENCRYPTION_UPDATE:
                        # The encryption state has changed (likely as a result of pairing or bonding).
                        conn_handle, encrypted, authenticated, bonded, key_size = data
                    elif event == _IRQ_GET_SECRET:
                        # Return a stored secret.
                        # If key is None, return the index'th value of this sec_type.
                        # Otherwise return the corresponding value for this sec_type and key.
                        sec_type, index, key = data
                        return value
                    elif event == _IRQ_SET_SECRET:
                        # Save a secret to the store for this sec_type and key.
                        sec_type, key, value = data
                        return True
                    elif event == _IRQ_PASSKEY_ACTION:
                        # Respond to a passkey request during pairing.
                        # See gap_passkey() for details.
                        # action will be an action that is compatible with the configured "io" config.
                        # passkey will be non-zero if action is "numeric comparison".
                        conn_handle, action, passkey = data


        The event codes are::

            from micropython import const
            _IRQ_CENTRAL_CONNECT = const(1)
            _IRQ_CENTRAL_DISCONNECT = const(2)
            _IRQ_GATTS_WRITE = const(3)
            _IRQ_GATTS_READ_REQUEST = const(4)
            _IRQ_SCAN_RESULT = const(5)
            _IRQ_SCAN_DONE = const(6)
            _IRQ_PERIPHERAL_CONNECT = const(7)
            _IRQ_PERIPHERAL_DISCONNECT = const(8)
            _IRQ_GATTC_SERVICE_RESULT = const(9)
            _IRQ_GATTC_SERVICE_DONE = const(10)
            _IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
            _IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
            _IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
            _IRQ_GATTC_DESCRIPTOR_DONE = const(14)
            _IRQ_GATTC_READ_RESULT = const(15)
            _IRQ_GATTC_READ_DONE = const(16)
            _IRQ_GATTC_WRITE_DONE = const(17)
            _IRQ_GATTC_NOTIFY = const(18)
            _IRQ_GATTC_INDICATE = const(19)
            _IRQ_GATTS_INDICATE_DONE = const(20)
            _IRQ_MTU_EXCHANGED = const(21)
            _IRQ_L2CAP_ACCEPT = const(22)
            _IRQ_L2CAP_CONNECT = const(23)
            _IRQ_L2CAP_DISCONNECT = const(24)
            _IRQ_L2CAP_RECV = const(25)
            _IRQ_L2CAP_SEND_READY = const(26)
            _IRQ_CONNECTION_UPDATE = const(27)
            _IRQ_ENCRYPTION_UPDATE = const(28)
            _IRQ_GET_SECRET = const(29)
            _IRQ_SET_SECRET = const(30)

        For the ``_IRQ_GATTS_READ_REQUEST`` event, the available return codes are::

            _GATTS_NO_ERROR = const(0x00)
            _GATTS_ERROR_READ_NOT_PERMITTED = const(0x02)
            _GATTS_ERROR_WRITE_NOT_PERMITTED = const(0x03)
            _GATTS_ERROR_INSUFFICIENT_AUTHENTICATION = const(0x05)
            _GATTS_ERROR_INSUFFICIENT_AUTHORIZATION = const(0x08)
            _GATTS_ERROR_INSUFFICIENT_ENCRYPTION = const(0x0f)

        For the ``_IRQ_PASSKEY_ACTION`` event, the available actions are::

            _PASSKEY_ACTION_NONE = const(0)
            _PASSKEY_ACTION_INPUT = const(2)
            _PASSKEY_ACTION_DISPLAY = const(3)
            _PASSKEY_ACTION_NUMERIC_COMPARISON = const(4)

        In order to save space in the firmware, these constants are not included on the
        :mod:`ubluetooth` module. Add the ones that you need from the list above to your
        program.

        """
        ...

    # .. method:: BLE.gap_advertise(interval_us, adv_data=None, *, resp_data=None, connectable=True)
    def gap_advertise(self, interval_us, adv_data=None, *, resp_data=None, connectable=True) -> Any:
        """
        Starts advertising at the specified interval (in **micro**\ seconds). This
        interval will be rounded down to the nearest 625us. To stop advertising, set
        *interval_us* to ``None``.

        *adv_data* and *resp_data* can be any type that implements the buffer
        protocol (e.g. ``bytes``, ``bytearray``, ``str``). *adv_data* is included
        in all broadcasts, and *resp_data* is send in reply to an active scan.

        **Note:** if *adv_data* (or *resp_data*) is ``None``, then the data passed
        to the previous call to ``gap_advertise`` will be re-used. This allows a
        broadcaster to resume advertising with just ``gap_advertise(interval_us)``.
        To clear the advertising payload pass an empty ``bytes``, i.e. ``b''``.

        """
        ...

    # .. method:: BLE.gap_scan(duration_ms, interval_us=1280000, window_us=11250, active=False, /)
    def gap_scan(self, duration_ms, interval_us=1280000, window_us=11250, active=False, /) -> Any:
        """
        Run a scan operation lasting for the specified duration (in **milli**\ seconds).

        To scan indefinitely, set *duration_ms* to ``0``.

        To stop scanning, set *duration_ms* to ``None``.

        Use *interval_us* and *window_us* to optionally configure the duty cycle.
        The scanner will run for *window_us* **micro**\ seconds every *interval_us*
        **micro**\ seconds for a total of *duration_ms* **milli**\ seconds. The default
        interval and window are 1.28 seconds and 11.25 milliseconds respectively
        (background scanning).

        For each scan result the ``_IRQ_SCAN_RESULT`` event will be raised, with event
        data ``(addr_type, addr, adv_type, rssi, adv_data)``.

        ``addr_type`` values indicate public or random addresses:
            * 0x00 - PUBLIC
            * 0x01 - RANDOM (either static, RPA, or NRPA, the type is encoded in the address itself)

        ``adv_type`` values correspond to the Bluetooth Specification:

            * 0x00 - ADV_IND - connectable and scannable undirected advertising
            * 0x01 - ADV_DIRECT_IND - connectable directed advertising
            * 0x02 - ADV_SCAN_IND - scannable undirected advertising
            * 0x03 - ADV_NONCONN_IND - non-connectable undirected advertising
            * 0x04 - SCAN_RSP - scan response

        ``active`` can be set ``True`` if you want to receive scan responses in the results.

        When scanning is stopped (either due to the duration finishing or when
        explicitly stopped), the ``_IRQ_SCAN_DONE`` event will be raised.

        """
        ...

    # .. method:: BLE.gap_connect(addr_type, addr, scan_duration_ms=2000, /)
    def gap_connect(self, addr_type, addr, scan_duration_ms=2000, /) -> Any:
        """
        Connect to a peripheral.

        See :meth:`gap_scan <BLE.gap_scan>` for details about address types.

        On success, the ``_IRQ_PERIPHERAL_CONNECT`` event will be raised.

        """
        ...

    # .. method:: BLE.gap_disconnect(conn_handle, /)
    def gap_disconnect(self, conn_handle, /) -> Any:
        """
        Disconnect the specified connection handle. This can either be a
        central that has connected to this device (if acting as a peripheral)
        or a peripheral that was previously connected to by this device (if acting
        as a central).

        On success, the ``_IRQ_PERIPHERAL_DISCONNECT`` or ``_IRQ_CENTRAL_DISCONNECT``
        event will be raised.

        Returns ``False`` if the connection handle wasn't connected, and ``True``
        otherwise.

        """
        ...

    # .. method:: BLE.gatts_register_services(services_definition, /)
    def gatts_register_services(self, services_definition, /) -> Any:
        """
        Configures the server with the specified services, replacing any
        existing services.

        *services_definition* is a list of **services**, where each **service** is a
        two-element tuple containing a UUID and a list of **characteristics**.

        Each **characteristic** is a two-or-three-element tuple containing a UUID, a
        **flags** value, and optionally a list of *descriptors*.

        Each **descriptor** is a two-element tuple containing a UUID and a **flags**
        value.

        The **flags** are a bitwise-OR combination of the flags defined below. These
        set both the behaviour of the characteristic (or descriptor) as well as the
        security and privacy requirements.

        The return value is a list (one element per service) of tuples (each element
        is a value handle). Characteristics and descriptor handles are flattened
        into the same tuple, in the order that they are defined.

        The following example registers two services (Heart Rate, and Nordic UART)::

            HR_UUID = bluetooth.UUID(0x180D)
            HR_CHAR = (bluetooth.UUID(0x2A37), bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,)
            HR_SERVICE = (HR_UUID, (HR_CHAR,),)
            UART_UUID = bluetooth.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
            UART_TX = (bluetooth.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E'), bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,)
            UART_RX = (bluetooth.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E'), bluetooth.FLAG_WRITE,)
            UART_SERVICE = (UART_UUID, (UART_TX, UART_RX,),)
            SERVICES = (HR_SERVICE, UART_SERVICE,)
            ( (hr,), (tx, rx,), ) = bt.gatts_register_services(SERVICES)

        The three value handles (``hr``, ``tx``, ``rx``) can be used with
        :meth:`gatts_read <BLE.gatts_read>`, :meth:`gatts_write <BLE.gatts_write>`, :meth:`gatts_notify <BLE.gatts_notify>`, and
        :meth:`gatts_indicate <BLE.gatts_indicate>`.

        **Note:** Advertising must be stopped before registering services.

        Available flags for characteristics and descriptors are::

            from micropython import const
            _FLAG_BROADCAST = const(0x0001)
            _FLAG_READ = const(0x0002)
            _FLAG_WRITE_NO_RESPONSE = const(0x0004)
            _FLAG_WRITE = const(0x0008)
            _FLAG_NOTIFY = const(0x0010)
            _FLAG_INDICATE = const(0x0020)
            _FLAG_AUTHENTICATED_SIGNED_WRITE = const(0x0040)

            _FLAG_AUX_WRITE = const(0x0100)
            _FLAG_READ_ENCRYPTED = const(0x0200)
            _FLAG_READ_AUTHENTICATED = const(0x0400)
            _FLAG_READ_AUTHORIZED = const(0x0800)
            _FLAG_WRITE_ENCRYPTED = const(0x1000)
            _FLAG_WRITE_AUTHENTICATED = const(0x2000)
            _FLAG_WRITE_AUTHORIZED = const(0x4000)

        As for the IRQs above, any required constants should be added to your Python code.
        """
        ...

    # .. method:: BLE.gatts_write(value_handle, data, /)
    def gatts_write(self, value_handle, data, /) -> Any:
        """
        Writes the local value for this handle, which can be read by a client.
        """
        ...

    # .. method:: BLE.gatts_indicate(conn_handle, value_handle, /)
    def gatts_indicate(self, conn_handle, value_handle, /) -> Any:
        """
        Sends an indication request to a connected client.

        **Note:** This does not currently support sending a custom value, it will
        always send the current local value (as set with :meth:`gatts_write
        <BLE.gatts_write>`).

        On acknowledgment (or failure, e.g. timeout), the
        ``_IRQ_GATTS_INDICATE_DONE`` event will be raised.
        """
        ...

    # .. method:: BLE.gattc_discover_services(conn_handle, uuid=None, /)
    def gattc_discover_services(self, conn_handle, uuid=None, /) -> Any:
        """
        Query a connected server for its services.

        Optionally specify a service *uuid* to query for that service only.

        For each service discovered, the ``_IRQ_GATTC_SERVICE_RESULT`` event will
        be raised, followed by ``_IRQ_GATTC_SERVICE_DONE`` on completion.
        """
        ...

    # .. method:: BLE.gattc_discover_descriptors(conn_handle, start_handle, end_handle, /)
    def gattc_discover_descriptors(self, conn_handle, start_handle, end_handle, /) -> Any:
        """
        Query a connected server for descriptors in the specified range.

        For each descriptor discovered, the ``_IRQ_GATTC_DESCRIPTOR_RESULT`` event
        will be raised, followed by ``_IRQ_GATTC_DESCRIPTOR_DONE`` on completion.
        """
        ...

    # .. method:: BLE.gattc_write(conn_handle, value_handle, data, mode=0, /)
    def gattc_write(self, conn_handle, value_handle, data, mode=0, /) -> Any:
        """
        Issue a remote write to a connected server for the specified
        characteristic or descriptor handle.

        The argument *mode* specifies the write behaviour, with the currently
        supported values being:

            * ``mode=0`` (default) is a write-without-response: the write will
              be sent to the remote server but no confirmation will be
              returned, and no event will be raised.
            * ``mode=1`` is a write-with-response: the remote server is
              requested to send a response/acknowledgement that it received the
              data.

        If a response is received from the remote server the
        ``_IRQ_GATTC_WRITE_DONE`` event will be raised.
        """
        ...

    # .. method:: BLE.l2cap_listen(psm, mtu, /)
    def l2cap_listen(self, psm, mtu, /) -> Any:
        """
        Start listening for incoming L2CAP channel requests on the specified *psm*
        with the local MTU set to *mtu*.

        When a remote device initiates a connection, the ``_IRQ_L2CAP_ACCEPT``
        event will be raised, which gives the listening server a chance to reject
        the incoming connection (by returning a non-zero integer).

        Once the connection is accepted, the ``_IRQ_L2CAP_CONNECT`` event will be
        raised, allowing the server to obtain the channel id (CID) and the local and
        remote MTU.

        **Note:** It is not currently possible to stop listening.
        """
        ...

    # .. method:: BLE.l2cap_disconnect(conn_handle, cid, /)
    def l2cap_disconnect(self, conn_handle, cid, /) -> Any:
        """
        Disconnect an active L2CAP channel with the specified *conn_handle* and
        *cid*.
        """
        ...

    # .. method:: BLE.l2cap_recvinto(conn_handle, cid, buf, /)
    def l2cap_recvinto(self, conn_handle, cid, buf, /) -> Any:
        """
        Receive data from the specified *conn_handle* and *cid* into the provided
        *buf* (which must support the buffer protocol, e.g. bytearray or
        memoryview).

        Returns the number of bytes read from the channel.

        If *buf* is None, then returns the number of bytes available.

        **Note:** After receiving the ``_IRQ_L2CAP_RECV`` event, the application should
        continue calling :meth:`l2cap_recvinto <BLE.l2cap_recvinto>` until no more
        bytes are available in the receive buffer (typically up to the size of the
        remote (peer) MTU).

        Until the receive buffer is empty, the remote device will not be granted
        more channel credits and will be unable to send any more data.

        """
        ...

    # .. method:: BLE.gap_pair(conn_handle, /)
    def gap_pair(self, conn_handle, /) -> Any:
        """
        Initiate pairing with the remote device.

        Before calling this, ensure that the ``io``, ``mitm``, ``le_secure``, and
        ``bond`` configuration options are set (via :meth:`config<BLE.config>`).

        On successful pairing, the ``_IRQ_ENCRYPTION_UPDATE`` event will be raised.
        """
        ...

    # .. class:: UUID(value, /)
    # .. class:: UUID(value, /)

    # class:: UUID
    class UUID:
        """
        Creates a UUID instance with the specified **value**.

        The **value** can be either:

        - A 16-bit integer. e.g. ``0x2908``.
        - A 128-bit UUID string. e.g. ``'6E400001-B5A3-F393-E0A9-E50E24DCCA9E'``.
        """

        def __init__(self, value, /) -> None:
            ...
