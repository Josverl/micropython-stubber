# board : ESP32
# ref : https://docs.micropython.org/en/latest/esp32/quickref.html

# SD card
import machine, os

# Slot 2 uses pins sck=18, cs=5, miso=19, mosi=23
sd = machine.SDCard(slot=1)

os.mount(sd, "/sd")  # mount
os.listdir("/sd")  # list directory contents
os.umount("/sd")  # eject



# DS18S20 and DS18B20 devices:

import ds18x20

ds = ds18x20.DS18X20(ow)
roms = ds.scan()
ds.convert_temp()
time.sleep_ms(750)
for rom in roms:
    print(ds.read_temp(rom))


# Capacitive touch

from machine import TouchPad, Pin

t = TouchPad(Pin(14))
t.read()  # Returns a smaller number when touched
