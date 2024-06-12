"""Module for handling the bootloader mode for micropython boards"""

from mpflash.mpremoteboard import MPRemoteBoard


def enter_bootloader_mpy(mcu: MPRemoteBoard, timeout: int = 10):
    """Enter the bootloader mode for the board using mpremote and micropython on the board"""
    mcu.run_command("bootloader", timeout=timeout)
    # todo: check if mpremote command was successful
    return True
