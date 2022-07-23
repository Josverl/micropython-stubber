# Neopixel
import esp
from machine import Pin

# For low-level driving of a NeoPixel:
pin = Pin(18)
grb_buf = (1, 20, 2, 40)
is800khz = False

# Note: ESP8266 only
# TODO: Is not resolved yet
esp.neopixel_write(pin, grb_buf, is800khz)
