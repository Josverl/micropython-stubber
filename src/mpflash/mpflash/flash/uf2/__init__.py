"""
Flash SAMD and RP2 via UF2
"""

import shutil
import sys
from pathlib import Path
from typing import Optional

import tenacity
from loguru import logger as log

from tenacity import stop_after_attempt, wait_fixed

from mpflash.mpremoteboard import MPRemoteBoard

from mpflash.common import PORT_FWTYPES
from .boardid import get_board_id
from .linux import dismount_uf2_linux, wait_for_UF2_linux
from .macos import wait_for_UF2_macos
from .windows import wait_for_UF2_windows


def flash_uf2(mcu: MPRemoteBoard, fw_file: Path, erase: bool) -> Optional[MPRemoteBoard]:
    """
    Flash .UF2 devices via bootloader and filecopy
    - mpremote bootloader
    - Wait for the device to mount as a drive (up to 5s)
    - detect new drive with INFO_UF2.TXT
    - copy the firmware file to the drive
    - wait for the device to restart (5s)

    for Linux - to support headless operation ( GH Actions ) :
        pmount and pumount are used to mount and unmount the drive
        as this is not done automatically by the OS in headless mode.
    """
    if ".uf2" not in PORT_FWTYPES[mcu.port]:
        log.error(f"UF2 not supported on {mcu.board} on {mcu.serialport}")
        return None
    if erase:
        log.warning("Erase not (yet) supported on .UF2, skipping erase.")

    destination = waitfor_uf2(board_id=mcu.port.upper())

    if not destination or not destination.exists() or not (destination / "INFO_UF2.TXT").exists():
        log.error("Board is not in bootloader mode")
        return None

    log.info("Board is in bootloader mode")
    board_id = get_board_id(destination)  # type: ignore
    log.info(f"Board ID: {board_id}")
    try:
        copy_firmware_to_uf2(fw_file, destination)
        log.success("Done copying, resetting the board.")
    except tenacity.RetryError:
        log.error("Failed to copy the firmware file to the board.")
        return None

    if sys.platform in ["linux"]:
        dismount_uf2_linux()

    mcu.wait_for_restart()
    return mcu


def waitfor_uf2(board_id: str):
    """
    Wait for the UF2 drive to mount
    """
    if sys.platform == "linux":
        return wait_for_UF2_linux(board_id=board_id)
    elif sys.platform == "win32":
        return wait_for_UF2_windows(board_id=board_id)
    elif sys.platform == "darwin":
        return wait_for_UF2_macos(board_id=board_id)
    else:
        log.warning(f"OS {sys.platform} not tested/supported")
        return None


@tenacity.retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=False)
def copy_firmware_to_uf2(fw_file: Path, destination: Path):
    """
    Copy the firmware file to the destination,
    Retry 3 times with 1s delay
    """
    log.info(f"Copying {fw_file} to {destination}.")
    return shutil.copy(fw_file, destination)
