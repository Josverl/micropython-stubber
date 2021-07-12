from typing import Any, Optional, Union, Tuple

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
# .. function:: wake_on_touch(wake)
def wake_on_touch(wake) -> Any:
    """
        Configure whether or not a touch will wake the device from sleep.
        *wake* should be a boolean value.
    """
    ...


# .. function:: wake_on_ext0(pin, level)
def wake_on_ext0(pin, level) -> Any:
    """
        Configure how EXT0 wakes the device from sleep.  *pin* can be ``None``
        or a valid Pin object.  *level* should be ``esp32.WAKEUP_ALL_LOW`` or
        ``esp32.WAKEUP_ANY_HIGH``.
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


# .. function:: raw_temperature()
def raw_temperature() -> Any:
    """
        Read the raw value of the internal temperature sensor, returning an integer.
    """
    ...


# .. function:: hall_sensor()
def hall_sensor() -> Any:
    """
        Read the raw value of the internal Hall sensor, returning an integer.
    """
    ...


# .. function:: idf_heap_info(capabilities)
def idf_heap_info(capabilities) -> Any:
    """
        Returns information about the ESP-IDF heap memory regions. One of them contains
        the MicroPython heap and the others are used by ESP-IDF, e.g., for network
        buffers and other data. This data is useful to get a sense of how much memory
        is available to ESP-IDF and the networking stack in particular. It may shed
        some light on situations where ESP-IDF operations fail due to allocation failures.
        The information returned is *not* useful to troubleshoot Python allocation failures,
        use `micropython.mem_info()` instead.
    
        The capabilities parameter corresponds to ESP-IDF's ``MALLOC_CAP_XXX`` values but the
        two most useful ones are predefined as `esp32.HEAP_DATA` for data heap regions and
        `esp32.HEAP_EXEC` for executable regions as used by the native code emitter.
    
        The return value is a list of 4-tuples, where each 4-tuple corresponds to one heap
        and contains: the total bytes, the free bytes, the largest free block, and
        the minimum free seen over time.
    
        Example after booting::
    
            >>> import esp32; esp32.idf_heap_info(esp32.HEAP_DATA)
            [(240, 0, 0, 0), (7288, 0, 0, 0), (16648, 4, 4, 4), (79912, 35712, 35512, 35108),
             (15072, 15036, 15036, 15036), (113840, 0, 0, 0)]
    """
    ...


# .. class:: Partition(id)
# class:: Partition
class Partition:
    """
        Create an object representing a partition.  *id* can be a string which is the label
        of the partition to retrieve, or one of the constants: ``BOOT`` or ``RUNNING``.
    """
    def __init__(self, id) -> None:
        ...

# .. classmethod:: Partition.find(type=TYPE_APP, subtype=0xff, label=None)
    @classmethod
    def find(cls, type=TYPE_APP, subtype=0xff, label=None) -> Any:
        """
            Find a partition specified by *type*, *subtype* and *label*.  Returns a
            (possibly empty) list of Partition objects. Note: ``subtype=0xff`` matches any subtype
            and ``label=None`` matches any label.
        """
        ...

# .. method:: Partition.info()
    def info(self, ) -> Any:
        """
            Returns a 6-tuple ``(type, subtype, addr, size, label, encrypted)``.
        """
        ...

# .. method:: Partition.readblocks(block_num, buf)
    def readblocks(self, block_num, buf) -> Any:
        """
                    Partition.readblocks(block_num, buf, offset)
        """
        ...

# .. method:: Partition.writeblocks(block_num, buf)
    def writeblocks(self, block_num, buf) -> Any:
        """
                    Partition.writeblocks(block_num, buf, offset)
        """
        ...

# .. method:: Partition.ioctl(cmd, arg)
    def ioctl(self, cmd, arg) -> Any:
        """
            These methods implement the simple and :ref:`extended
            <block-device-interface>` block protocol defined by
            :class:`uos.AbstractBlockDev`.
        """
        ...

# .. method:: Partition.set_boot()
    def set_boot(self, ) -> Any:
        """
            Sets the partition as the boot partition.
        """
        ...

# .. method:: Partition.get_next_update()
    def get_next_update(self, ) -> Any:
        """
            Gets the next update partition after this one, and returns a new Partition object.
            Typical usage is ``Partition(Partition.RUNNING).get_next_update()``
            which returns the next partition to update given the current running one.
        """
        ...

# .. classmethod:: Partition.mark_app_valid_cancel_rollback()
    @classmethod
    def mark_app_valid_cancel_rollback(cls, ) -> Any:
        """
            Signals that the current boot is considered successful.
            Calling ``mark_app_valid_cancel_rollback`` is required on the first boot of a new
            partition to avoid an automatic rollback at the next boot.
            This uses the ESP-IDF "app rollback" feature with "CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE"
            and  an ``OSError(-261)`` is raised if called on firmware that doesn't have the
            feature enabled.
            It is OK to call ``mark_app_valid_cancel_rollback`` on every boot and it is not
            necessary when booting firmare that was loaded using esptool.
        """
        ...

# .. data:: Partition.BOOT
# .. data:: Partition.TYPE_APP
# .. data:: HEAP_DATA
# .. Warning::
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
    def __init__(self, channel, *, pin=None, clock_div=8, idle_level=False, tx_carrier=None) -> None:
        ...

# .. method:: RMT.source_freq()
    def source_freq(self, ) -> Any:
        """
            Returns the source clock frequency. Currently the source clock is not
            configurable so this will always return 80MHz.
        """
        ...

# .. method:: RMT.clock_div()
    def clock_div(self, ) -> Any:
        """
            Return the clock divider. Note that the channel resolution is
            ``1 / (source_freq / clock_div)``.
        """
        ...

# .. method:: RMT.wait_done(*, timeout=0)
    def wait_done(self, *, timeout=0) -> Any:
        """
            Returns ``True`` if the channel is idle or ``False`` if a sequence of
            pulses started with `RMT.write_pulses` is being transmitted. If the
            *timeout* keyword argument is given then block for up to this many
            milliseconds for transmission to complete.
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

# .. method:: RMT.write_pulses(duration, data=True)
    def write_pulses(self, duration, data=True) -> Any:
        """
            Begin transmitting a sequence. There are three ways to specify this:
        
            **Mode 1:** *duration* is a list or tuple of durations. The optional *data*
            argument specifies the initial output level. The output level will toggle
            after each duration.
        
            **Mode 2:** *duration* is a positive integer and *data* is a list or tuple
            of output levels. *duration* specifies a fixed duration for each.
        
            **Mode 3:** *duration* and *data* are lists or tuples of equal length,
            specifying individual durations and the output level for each.
        
            Durations are in integer units of the channel resolution (as described
            above), between 1 and 32767 units. Output levels are any value that can
            be converted to a boolean, with ``True`` representing high voltage and
            ``False`` representing low.
        
            If transmission of an earlier sequence is in progress then this method will
            block until that transmission is complete before beginning the new sequence.
        
            If looping has been enabled with `RMT.loop`, the sequence will be
            repeated indefinitely. Further calls to this method will block until the
            end of the current loop iteration before immediately beginning to loop the
            new sequence of pulses. Looping sequences longer than 126 pulses is not
            supported by the hardware.
        
        """
        ...

# .. class:: ULP()
# class:: ULP
class ULP:
    """
        This class provides access to the Ultra-Low-Power co-processor.
    """
    def __init__(self, ) -> None:
        ...

# .. method:: ULP.set_wakeup_period(period_index, period_us)
    def set_wakeup_period(self, period_index, period_us) -> Any:
        """
            Set the wake-up period.
        """
        ...

# .. method:: ULP.load_binary(load_addr, program_binary)
    def load_binary(self, load_addr, program_binary) -> Any:
        """
            Load a *program_binary* into the ULP at the given *load_addr*.
        """
        ...

# .. method:: ULP.run(entry_point)
    def run(self, entry_point) -> Any:
        """
            Start the ULP running at the given *entry_point*.
        
        """
        ...

# .. data:: esp32.WAKEUP_ALL_LOW
# .. warning::
# .. class:: NVS(namespace)
# class:: NVS
class NVS:
    """
        Create an object providing access to a namespace (which is automatically created if not
        present).
    """
    def __init__(self, namespace) -> None:
        ...

# .. method:: NVS.set_i32(key, value)
    def set_i32(self, key, value) -> Any:
        """
            Sets a 32-bit signed integer value for the specified key. Remember to call *commit*!
        """
        ...

# .. method:: NVS.get_i32(key)
    def get_i32(self, key) -> Any:
        """
            Returns the signed integer value for the specified key. Raises an OSError if the key does not
            exist or has a different type.
        """
        ...

# .. method:: NVS.set_blob(key, value)
    def set_blob(self, key, value) -> Any:
        """
            Sets a binary blob value for the specified key. The value passed in must support the buffer
            protocol, e.g. bytes, bytearray, str. (Note that esp-idf distinguishes blobs and strings, this
            method always writes a blob even if a string is passed in as value.)
            Remember to call *commit*!
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

# .. method:: NVS.erase_key(key)
    def erase_key(self, key) -> Any:
        """
            Erases a key-value pair.
        """
        ...

# .. method:: NVS.commit()
    def commit(self, ) -> Any:
        """
            Commits changes made by *set_xxx* methods to flash.
        """
        ...

