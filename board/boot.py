# This file is executed on every boot (including wake-boot from deepsleep)
import machine
import uos as os

try:
    import esp

    esp.osdebug(None)
except:
    pass

try:
    import pyb

    pyb.country("US")  # ISO 3166-1 Alpha-2 code, eg US, GB, DE, AU
    pyb.usb_mode("VCP+MSC")  # act as a serial and a storage device
    # pyb.main('main.py') # main script to run after this one
    # pyb.usb_mode('VCP+HID') # act as a serial device and a mouse
except:
    pass

SD = False
if SD:
    # Mount SD to /sd
    try:
        # Some boards have pulldown and/or LED on GPIO2, pullup avoids issues on TTGO 8 v1.8
        # machine.Pin(2,mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)
        # os.mount(machine.SDCard(slot=1, width=4), "/sd")  # SD mode 4 bit
        if esp:
            # # SPI 1 bit M5Stack Core
            os.mount(machine.SDCard(slot=2, width=1, sck=18, miso=19, mosi=23, cs=4), "/sd")  # SPI 1 bit M5Stack Core
            print("SD Card mounted")
    except OSError as e:
        if e.args[0] == 16:
            print("No SD Card found")
