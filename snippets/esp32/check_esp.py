# ref: https://docs.micropython.org/en/latest/esp8266/quickref.html
# The esp module:
from machine import Pin
import esp

esp.osdebug(None)  # turn off vendor O/S debugging messages
esp.osdebug(0)  # redirect vendor O/S debugging messages to UART(0)


sector_no = 1  # Placeholders
byte_offset = 0
buffer = b"0000"

# low level methods to interact with flash storage
esp.flash_size()
esp.flash_user_start()
esp.flash_erase(sector_no)
esp.flash_write(byte_offset, buffer)
esp.flash_read(byte_offset, buffer)

# Neopixel
# # Note: ESP8266 only

# import esp
# # For low-level driving of a NeoPixel:
# pin = Pin(18)
# grb_buf = (1, 20, 2, 40)
# is800khz = False
# esp.neopixel_write(pin, grb_buf, is800khz)  # type: ignore
