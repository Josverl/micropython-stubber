# board : ESP32
# ref : https://docs.micropython.org/en/latest/esp32/quickref.html
import machine

# Deep-sleep mode


# check if the device woke from a deep sleep
if machine.reset_cause() == machine.DEEPSLEEP_RESET:  # type: ignore - not on all ports
    print("woke from a deep sleep")

# put the device to deep sleep for 10 seconds

machine.deepsleep(10000)
# detect that deep sleep never returns
assert False, "Deep sleep never returns"
