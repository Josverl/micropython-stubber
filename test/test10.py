# pylint shows an error for time and not for utime
# No name 'sleep_ms' in module 'time'
from time import sleep_ms
sleep_ms(2)

# "Module 'time' has no 'ticks_base' member"
import time
time.ticks_base()

from utime import sleep_us, block_sleep
import utime
sleep_us(1)
block_sleep(3)

utime.ticks_base()

