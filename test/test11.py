# pylint shows an error for time 
# No name 'sleep_ms' in module 'time'
from time import sleep_ms
sleep_ms(2)

# "Module 'time' has no 'ticks_base' member"
import time
time.ticks_base() 



