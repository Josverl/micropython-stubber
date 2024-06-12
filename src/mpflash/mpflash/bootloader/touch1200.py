import sys
import time

import serial

from mpflash.errors import MPFlashError
from mpflash.logger import log
from mpflash.mpremoteboard import MPRemoteBoard

from .manual import enter_bootloader_manual


def enter_bootloader_cdc_1200bps(mcu: MPRemoteBoard, timeout: int = 10):
    if sys.platform == "win32":
        log.warning("Touch 1200bps method is currently not supported on Windows, switching to manual")
        return enter_bootloader_manual(mcu, timeout=timeout)

    log.info(f"Entering bootloader on {mcu.board} on {mcu.serialport} using CDC 1200bps")
    # if port argument is present perform soft reset
    if not mcu.serialport:
        raise MPFlashError("No serial port specified")
    # try to initiate serial port connection on PORT with 1200 baudrate
    try:
        with serial.Serial(
            port=mcu.serialport,
            baudrate=1200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            rtscts=True,
        ) as connection:
            print("Connection established")
            connection.rts = True
            connection.dtr = False
            time.sleep(0.4)

    except serial.SerialException as e:
        log.exception(e)
        raise MPFlashError("pySerial error: " + str(e) + "\n") from e
    except Exception as e:
        log.exception(e)
        raise MPFlashError("Error: " + str(e) + "\n") from e

    # be optimistic
    return True
