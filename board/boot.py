# This file is executed on every boot (including wake-boot from deepsleep)
import esp
import machine
import uos as os

esp.osdebug(None)

SD = False
if SD:
    # Mount SD to /sd
    try:
        # Some boards have pulldown and/or LED on GPIO2, pullup avoids issues on TTGO 8 v1.8
        # machine.Pin(2,mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)
        # os.mount(machine.SDCard(slot=1, width=4), "/sd")  # SD mode 4 bit

        # # SPI 1 bit M5Stack Core
        os.mount(machine.SDCard(slot=2, width=1, sck=18, miso=19, mosi=23, cs=4), "/sd")  # SPI 1 bit M5Stack Core
        print("SD Card mounted")
    except OSError as e:
        if e.args[0] == 16:
            print("No SD Card found")
