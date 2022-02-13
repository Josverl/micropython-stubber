# The esp module:

import esp

esp.osdebug(None)  # turn off vendor O/S debugging messages
esp.osdebug(0)  # redirect vendor O/S debugging messages to UART(0)

sector_no = 1  # Placeholders
byte_offset = 0
buffer = [0]

# low level methods to interact with flash storage
esp.flash_size()
esp.flash_user_start()
esp.flash_erase(sector_no)
esp.flash_write(byte_offset, buffer)
esp.flash_read(byte_offset, buffer)

# The esp32 module:
import esp32

esp32.hall_sensor()  # read the internal hall sensor
esp32.raw_temperature()  # read the internal temperature of the MCU, in Fahrenheit
esp32.ULP()  # access to the Ultra-Low-Power Co-processor


# RMT

import esp32
from machine import Pin

r = esp32.RMT(0, pin=Pin(18), clock_div=8)
r  # RMT(channel=0, pin=18, source_freq=80000000, clock_div=8)
# The channel resolution is 100ns (1/(source_freq/clock_div)).
r.write_pulses((1, 20, 2, 40), 0)  # Send 0 for 100ns, 1 for 2000ns, 0 for 200ns, 1 for 4000ns


# For low-level driving of a NeoPixel:
pin = Pin(18)
grb_buf = (1, 20, 2, 40)
is800khz = False

import esp

# FIXME: Why is esp.neopixel_write not stubbed ?
# Note: there is a neopixel_write-stub module installed in the venv
esp.neopixel_write(pin, grb_buf, is800khz)  # type: ignore


## esp32/modules/flashbdev.py

from esp32 import Partition

# MicroPython's partition table uses "vfs", TinyUF2 uses "ffat".
bdev = Partition.find(Partition.TYPE_DATA, label="vfs")
if not bdev:
    bdev = Partition.find(Partition.TYPE_DATA, label="ffat")
bdev = bdev[0] if bdev else None
