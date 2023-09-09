# board : ESP32
# ref : https://docs.micropython.org/en/latest/esp32/quickref.html
# Deep-sleep mode
from typing_extensions import assert_never, assert_type
import machine

# check if the device woke from a deep sleep
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    assert_type(machine.reset_cause(), int)
    print("woke from a deep sleep")

machine.lightsleep(10000)

# put the device to sleep for 10 seconds
machine.deepsleep(10000)
assert_never("code after deepsleep() is never executed")
