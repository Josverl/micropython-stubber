# ref: https://docs.micropython.org/en/latest/esp8266/quickref.html
# The machine module:

import machine

freq = machine.freq()  # get the current frequency of the CPU
machine.freq(160000000)  # set the CPU frequency to 160 MHz
