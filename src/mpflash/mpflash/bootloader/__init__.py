import time

from mpflash.common import BootloaderMethod
from mpflash.errors import MPFlashError
from mpflash.logger import log
from mpflash.mpremoteboard import MPRemoteBoard

from .manual import enter_bootloader_manual
from .micropython import enter_bootloader_mpy
from .touch1200 import enter_bootloader_cdc_1200bps


def enter_bootloader(
    mcu: MPRemoteBoard,
    method: BootloaderMethod = BootloaderMethod.MPY,
    timeout: int = 10,
    wait_after: int = 2,
):
    """Enter the bootloader mode for the board"""
    if method == BootloaderMethod.NONE:
        # NO bootloader requested, so must be OK to flash
        return True

    log.info(f"Entering bootloader on {mcu.board} on {mcu.serialport} using method: {method.value}")
    if method == BootloaderMethod.MPY:
        result = enter_bootloader_mpy(mcu, timeout=timeout)
    elif method == BootloaderMethod.MANUAL:
        result = enter_bootloader_manual(mcu, timeout=timeout)
    elif method == BootloaderMethod.TOUCH_1200:
        result = enter_bootloader_cdc_1200bps(mcu, timeout=timeout)
    else:
        raise MPFlashError(f"Unknown bootloader method {method}")
    if result:
        time.sleep(wait_after)
    else:
        log.error(f"Failed to enter bootloader on {mcu.serialport}")
    return result
