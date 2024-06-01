"""
Flash SAMD and RP2 via UF2
"""

import shutil
import sys
import time
from pathlib import Path
from typing import Optional

from loguru import logger as log
from rich.progress import track

from mpflash.mpremoteboard import MPRemoteBoard

from .common import PORT_FWTYPES
from .flash_uf2_boardid import get_board_id
from .flash_uf2_linux import dismount_uf2_linux, wait_for_UF2_linux
from .flash_uf2_macos import wait_for_UF2_macos
from .flash_uf2_windows import wait_for_UF2_windows


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
        log.info("Erasing not yet implemented for UF2 flashing.")

    if sys.platform == "linux":
        destination = wait_for_UF2_linux()
    elif sys.platform == "win32":
        destination = wait_for_UF2_windows()
    elif sys.platform == "darwin":
        log.warning(f"OS {sys.platform} not tested/supported")
        destination = wait_for_UF2_macos()
    else:
        log.warning(f"OS {sys.platform} not tested/supported")
        return None

    if not destination or not destination.exists() or not (destination / "INFO_UF2.TXT").exists():
        log.error("Board is not in bootloader mode")
        return None

    log.info("Board is in bootloader mode")
    board_id = get_board_id(destination)  # type: ignore
    log.info(f"Board ID: {board_id}")
    log.info(f"Copying {fw_file} to {destination}.")
    shutil.copy(fw_file, destination)
    log.success("Done copying, resetting the board and wait for it to restart")
    if sys.platform in ["linux"]:
        dismount_uf2_linux()
    for _ in track(range(5 + 2), description="Waiting for the board to restart", transient=True, refresh_per_second=2):
        time.sleep(1)  # 5 secs to short on linux
    return mcu
