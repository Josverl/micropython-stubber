# This file is executed on every boot (including wake-boot from deepsleep)
import machine
import uos as os

try:
    import esp  # type: ignore

    esp.osdebug(None)
except ImportError:
    esp = None

try:
    import pyb  # type: ignore

    pyb.country("US")  # ISO 3166-1 Alpha-2 code, eg US, GB, DE, AU
    pyb.usb_mode("VCP+MSC")  # act as a serial and a storage device
    # pyb.main('main.py') # main script to run after this one
except ImportError:
    pass

MOUNT_SD = False
if MOUNT_SD:
    # Mount SD to /sd
    try:
        # Some boards have pulldown and/or LED on GPIO2, pullup avoids issues on TTGO 8 v1.8
        # machine.Pin(2,mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)
        # os.mount(machine.SDCard(slot=1, width=4), "/sd")  # SD mode 4 bit
        if esp:
            # # SPI 1 bit M5Stack Core
            os.mount(machine.SDCard(slot=2, width=1, sck=18, miso=19, mosi=23, cs=4), "/sd")  # type: ignore # SPI 1 bit M5Stack Core
            print("SD Card mounted")
    except OSError as e:
        if e.args[0] == 16:
            print("No SD Card found")
