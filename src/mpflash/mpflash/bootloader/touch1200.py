import sys
import time

import serial

from mpflash.errors import MPFlashError
from mpflash.logger import log
from mpflash.mpremoteboard import MPRemoteBoard



def enter_bootloader_cdc_1200bps(mcu: MPRemoteBoard, timeout: int = 10):
    if not mcu.serialport:
        raise MPFlashError("No serial port specified")
    log.info(f"Entering bootloader on {mcu.serialport} using CDC toch 1200 bps method")
    # if port argument is present perform soft reset
    # try to initiate serial port connection on PORT with 1200 baudrate
    try:
        com = serial.Serial(mcu.serialport, 1200, dsrdtr=True)
        com.rts = False  # required
        com.dtr = False  # might as well
        time.sleep(0.2)
        com.close()

    except serial.SerialException as e:
        log.exception(e)
        raise MPFlashError("pySerial error: " + str(e) + "\n") from e
    except Exception as e:
        log.exception(e)
        raise MPFlashError("Error: " + str(e) + "\n") from e

    # be optimistic
    return True
