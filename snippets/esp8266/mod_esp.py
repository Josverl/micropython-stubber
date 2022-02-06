# ref: https://docs.micropython.org/en/latest/esp8266/quickref.html
# The esp module:

import esp

esp.osdebug(None)       # turn off vendor O/S debugging messages
esp.osdebug(0)          # redirect vendor O/S debugging messages to UART(0)

