# Example using PIO to turn on an LED via an explicit exec.
#
# Demonstrates:
#   - using set_init and set_base
#   - using StateMachine.exec

import time

import rp2
from machine import Pin


# Define an empty program that uses a single set pin.
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)  # micropython-stubs>=1.20.0
def prog():
    pass


# Construct the StateMachine, binding Pin(25) to the set pin.
sm = rp2.StateMachine(0, prog, set_base=Pin(6))  # stubs-ignore: version<=1.20.0

# Turn on the set pin via an exec instruction.
sm.exec("set(pins, 1)")

# Sleep for 500ms.
time.sleep(0.5)

# Turn off the set pin via an exec instruction.
sm.exec("set(pins, 0)")
