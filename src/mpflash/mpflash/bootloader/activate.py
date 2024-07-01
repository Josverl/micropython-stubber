import time

from mpflash.bootloader.detect import in_bootloader
from mpflash.common import BootloaderMethod
from mpflash.errors import MPFlashError
from mpflash.logger import log
from mpflash.mpremoteboard import MPRemoteBoard

from .manual import enter_bootloader_manual
from .micropython import enter_bootloader_mpy
from .touch1200 import enter_bootloader_touch_1200bps

BL_OPTIONS = {
    "stm32": [BootloaderMethod.TOUCH_1200, BootloaderMethod.MPY, BootloaderMethod.MANUAL],
    "rp2": [BootloaderMethod.TOUCH_1200, BootloaderMethod.MPY, BootloaderMethod.MANUAL],
    "samd": [BootloaderMethod.TOUCH_1200, BootloaderMethod.MPY, BootloaderMethod.MANUAL],
    "esp32": [BootloaderMethod.NONE],
    "esp8266": [BootloaderMethod.NONE],
}


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
    elif method == BootloaderMethod.AUTO:
        # build a list of options to try for this board
        bl_list = BL_OPTIONS.get(mcu.port, [BootloaderMethod.MPY, BootloaderMethod.MANUAL])
    else:
        bl_list = [method, BootloaderMethod.MANUAL]
    log.info(f"Entering bootloader on {mcu.serialport} using methods {[bl.value for bl in bl_list]}")
    for method in bl_list:
        try:
            if method == BootloaderMethod.MPY:
                result = enter_bootloader_mpy(mcu, timeout=timeout)
            elif method == BootloaderMethod.MANUAL:
                result = enter_bootloader_manual(mcu, timeout=timeout)
            elif method == BootloaderMethod.TOUCH_1200:
                result = enter_bootloader_touch_1200bps(mcu, timeout=timeout)
        except MPFlashError as e:
            log.warning(f"Failed to enter bootloader on {mcu.serialport} using {method.value}")
            log.exception(e)
            result = False
        if not result:
            # try a next method
            continue

        # todo - check every second or so for up to max wait time
        time.sleep(wait_after)
        # check if bootloader was entered
        if in_bootloader(mcu):
            return True

    return result
