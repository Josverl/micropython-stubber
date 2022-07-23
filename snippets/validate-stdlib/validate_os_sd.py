"""
Code snippet used to validate the micropython stubs

machine.SDCard

Different implementations of the SDCard class on different hardware support varying options.
- Pyboard / stm32  : yes 
- ESP32 : yes 
- cc3200  : The current( 1.19) cc3200 SD card implementation names the this class machine.SD rather than machine.SDCard
- ESP8266 - not avaialble 

"""
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
