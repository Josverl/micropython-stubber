# SD card
import os
import machine
# Slot 2 uses pins sck=18, cs=5, miso=19, mosi=23
# sd = machine.SDCard(slot=2)
# Mount SD to /sd
sdcard = machine.SDCard(slot=2, width=1, sck=18, miso=19, mosi=23, cs=4)
os.mount(sdcard, "/sd")  # SPI 1 bit M5Stack Core
print("SD Card mounted")

sd = 1
os.mount(sd, "/sd")  # mount

os.listdir("/sd")  # list directory contents

os.umount("/sd")  # eject



# test is able to access uname named tuple
if os.uname().release == "1.13.0" and os.uname().version < "v1.13-103":
    raise NotImplementedError("MicroPython 1.13.0 cannot be stubbed")

u = os.uname()
print( u.sysname)
print( u.nodename)
print( u.release)
print( u.machine)
print( u.version)

