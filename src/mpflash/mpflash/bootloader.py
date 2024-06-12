import sys
import time
from enum import Enum

import serial

from mpflash.errors import MPFlashError
from mpflash.logger import log
from mpflash.mpremoteboard import MPRemoteBoard


class BootloaderMethod(Enum):
    MANUAL = "manual"
    MPY = "mpy"
    TOUCH_1200BPS = "touch1200bps"


def enter_bootloader(
    mcu: MPRemoteBoard,
    method: BootloaderMethod = BootloaderMethod.MPY,
    timeout: int = 10,
    wait_after: int = 2,
):
    """Enter the bootloader mode for the board"""

    if method == BootloaderMethod.MPY:
        return enter_bootloader_mpy(mcu, timeout=timeout, wait_after=wait_after)
    elif method == BootloaderMethod.MANUAL:
        return enter_bootloader_manual(mcu, timeout=timeout, wait_after=wait_after)
    elif method == BootloaderMethod.TOUCH_1200BPS:
        return enter_bootloader_cdc_1200bps(mcu, timeout=timeout, wait_after=wait_after)
    else:
        raise MPFlashError(f"Unknown bootloader method {method}")


def enter_bootloader_mpy(mcu: MPRemoteBoard, timeout: int = 10, wait_after: int = 2):
    """Enter the bootloader mode for the board"""
    log.info(f"Entering bootloader on {mcu.board} on {mcu.serialport}")
    mcu.run_command("bootloader", timeout=timeout)
    time.sleep(wait_after)


def enter_bootloader_manual(mcu: MPRemoteBoard, timeout: int = 10, wait_after: int = 2):

    message: str
    if mcu.port == "rp2":
        message = "Please Unplug the USB cable, press and hold the BOOTSEL button on the device, Plug the USB cable back in, and press Enter"
    elif mcu.port == "samd":
        message = "Please press the reset button twice in fast succession on the device, and press Enter"
    else:
        message = "Please press the reset button on the device and press Enter"

    input(message)
    return True


def enter_bootloader_cdc_1200bps(mcu: MPRemoteBoard, timeout: int = 10, wait_after: int = 2):

    if sys.platform == "win32":
        raise MPFlashError("Touch 1200bps method is currently not supported on Windows")

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

    time.sleep(0.4)
    return
