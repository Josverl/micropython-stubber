# SD card
import os

# Slot 2 uses pins sck=18, cs=5, miso=19, mosi=23
# sd = machine.SDCard(slot=2)
sd = 1
os.mount(sd, "/sd")  # mount

os.listdir("/sd")  # list directory contents

os.umount("/sd")  # eject


import uos 

