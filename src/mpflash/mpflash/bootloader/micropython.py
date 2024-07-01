"""Module for handling the bootloader mode for micropython boards"""

from mpflash.logger import log
from mpflash.mpremoteboard import MPRemoteBoard


def enter_bootloader_mpy(mcu: MPRemoteBoard, timeout: int = 10):
    """Enter the bootloader mode for the board using mpremote and micropython on the board"""
    log.info(f"Attempting bootloader on {mcu.serialport} using 'mpremote bootloader'")
    mcu.run_command("bootloader", timeout=timeout)
    # todo: check if mpremote command was successful
    return True
