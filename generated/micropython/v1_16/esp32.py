# .. currentmodule:: esp32
# currentmodule:: esp32
# .. module:: esp32
# origin: micropython\docs\library\esp32.rst
# v1.16
"""
    :synopsis: functionality specific to the ESP32

The ``esp32`` module contains functions and classes specifically aimed at
controlling ESP32 modules.

"""

from typing import Any, Optional, Union, Tuple

# .. module:: esp32
# .. function:: wake_on_touch(wake)
def wake_on_touch(wake) -> Any:
    """
    Configure whether or not a touch will wake the device from sleep.
    *wake* should be a boolean value.
    """
    ...


# .. function:: wake_on_ext1(pins, level)
def wake_on_ext1(pins, level) -> Any:
    """
    Configure how EXT1 wakes the device from sleep.  *pins* can be ``None``
    or a tuple/list of valid Pin objects.  *level* should be ``esp32.WAKEUP_ALL_LOW``
    or ``esp32.WAKEUP_ANY_HIGH``.
    """
    ...


# .. function:: hall_sensor()
def hall_sensor() -> Any:
    """
    Read the raw value of the internal Hall sensor, returning an integer.
    """
    ...


# .. class:: Partition(id)
# .. class:: Partition(id)

# class:: Partition
class Partition:
    """
    Create an object representing a partition.  *id* can be a string which is the label
    of the partition to retrieve, or one of the constants: ``BOOT`` or ``RUNNING``.
    """

    def __init__(self, id) -> None:
        ...

    # .. method:: Partition.info()
    def info(
        self,
    ) -> Any:
        """
        Returns a 6-tuple ``(type, subtype, addr, size, label, encrypted)``.
        """
        ...

    # .. method:: Partition.writeblocks(block_num, buf)
    def writeblocks(self, block_num, buf) -> Any:
        """
        Partition.writeblocks(block_num, buf, offset)
        """
        ...

    # .. method:: Partition.set_boot()
    def set_boot(
        self,
    ) -> Any:
        """
        Sets the partition as the boot partition.
        """
        ...

    # .. classmethod:: Partition.mark_app_valid_cancel_rollback()
    # .. data:: Partition.BOOT
    # .. data:: Partition.TYPE_APP
    # .. data:: HEAP_DATA
    # .. _esp32.RMT:
    # .. Warning::
    # .. class:: RMT(channel, *, pin=None, clock_div=8, idle_level=False, tx_carrier=None)
    # .. class:: RMT(channel, *, pin=None, clock_div=8, idle_level=False, tx_carrier=None)

    # class:: RMT
    class RMT:
        """
        This class provides access to one of the eight RMT channels. *channel* is
        required and identifies which RMT channel (0-7) will be configured. *pin*,
        also required, configures which Pin is bound to the RMT channel. *clock_div*
        is an 8-bit clock divider that divides the source clock (80MHz) to the RMT
        channel allowing the resolution to be specified. *idle_level* specifies
        what level the output will be when no transmission is in progress and can
        be any value that converts to a boolean, with ``True`` representing high
        voltage and ``False`` representing low.

        To enable the transmission carrier feature, *tx_carrier* should be a tuple
        of three positive integers: carrier frequency, duty percent (``0`` to
        ``100``) and the output level to apply the carrier to (a boolean as per
        *idle_level*).
        """

        def __init__(
            self, channel, *, pin=None, clock_div=8, idle_level=False, tx_carrier=None
        ) -> None:
            ...

        # .. method:: RMT.clock_div()
        def clock_div(
            self,
        ) -> Any:
            """
            Return the clock divider. Note that the channel resolution is
            ``1 / (source_freq / clock_div)``.
            """
            ...

        # .. method:: RMT.loop(enable_loop)
        def loop(self, enable_loop) -> Any:
            """
            Configure looping on the channel. *enable_loop* is bool, set to ``True`` to
            enable looping on the *next* call to `RMT.write_pulses`. If called with
            ``False`` while a looping sequence is currently being transmitted then the
            current loop iteration will be completed and then transmission will stop.
            """
            ...

        # .. class:: ULP()
        # .. class:: ULP()

        # class:: ULP
        class ULP:
            """
            This class provides access to the Ultra-Low-Power co-processor.
            """

            def __init__(
                self,
            ) -> None:
                ...

            # .. method:: ULP.load_binary(load_addr, program_binary)
            def load_binary(self, load_addr, program_binary) -> Any:
                """
                Load a *program_binary* into the ULP at the given *load_addr*.
                """
                ...

            # .. data:: esp32.WAKEUP_ALL_LOW
            # .. warning::
            # .. class:: NVS(namespace)
            # .. class:: NVS(namespace)

            # class:: NVS
            class NVS:
                """
                Create an object providing access to a namespace (which is automatically created if not
                present).
                """

                def __init__(self, namespace) -> None:
                    ...

                # .. method:: NVS.get_i32(key)
                def get_i32(self, key) -> Any:
                    """
                    Returns the signed integer value for the specified key. Raises an OSError if the key does not
                    exist or has a different type.
                    """
                    ...

                # .. method:: NVS.get_blob(key, buffer)
                def get_blob(self, key, buffer) -> Any:
                    """
                    Reads the value of the blob for the specified key into the buffer, which must be a bytearray.
                    Returns the actual length read. Raises an OSError if the key does not exist, has a different
                    type, or if the buffer is too small.
                    """
                    ...

                # .. method:: NVS.commit()
                def commit(
                    self,
                ) -> Any:
                    """
                    Commits changes made by *set_xxx* methods to flash.
                    """
                    ...
