import time
from pathlib import Path

from loguru import logger as log

from mpflash.mpremoteboard import MPRemoteBoard

from .flash_esp import flash_esp
from .flash_stm32 import flash_stm32
from .flash_uf2 import flash_uf2
from .worklist import WorkList

# #########################################################################################################


def flash_list(
    todo: WorkList,
    fw_folder: Path,
    erase: bool,
    bootloader: bool,
):
    """Flash a list of boards with the specified firmware."""
    flashed = []
    for mcu, fw_info in todo:
        fw_file = fw_folder / fw_info["filename"]  # type: ignore
        if not fw_file.exists():
            log.error(f"File {fw_file} does not exist, skipping {mcu.board} on {mcu.serialport}")
            continue
        log.info(f"Updating {mcu.board} on {mcu.serialport} to {fw_info['version']}")
        updated = None
        # try:
        if mcu.port in ["samd", "rp2", "nrf"]:  #  [k for k, v in PORT_FWTYPES.items() if v == ".uf2"]:
            if bootloader:
                enter_bootloader(mcu)
            updated = flash_uf2(mcu, fw_file=fw_file, erase=erase)
        elif mcu.port in ["stm32"]:
            if bootloader:
                enter_bootloader(mcu)
            updated = flash_stm32(mcu, fw_file, erase=erase)
        elif mcu.port in ["esp32", "esp8266"]:
            #  bootloader is handled by esptool for esp32/esp8266
            updated = flash_esp(mcu, fw_file=fw_file, erase=erase)
        else:
            log.error(f"Don't (yet) know how to flash {mcu.port}-{mcu.board} on {mcu.serialport}")

        if updated:
            flashed.append(updated)
        else:
            log.error(f"Failed to flash {mcu.board} on {mcu.serialport}")


def enter_bootloader(mcu: MPRemoteBoard, timeout: int = 10, wait_after: int = 2):
    """Enter the bootloader mode for the board"""
    log.info(f"Entering bootloader on {mcu.board} on {mcu.serialport}")
    mcu.run_command("bootloader", timeout=timeout)
    time.sleep(wait_after)


# TODO:
# flash from some sort of queue to allow different images to be flashed to the same board
#  - flash variant 1
#  - stub variant 1
#  - flash variant 2
#  - stub variant 2
#
# JIT download / download any missing firmwares based on the detected boards
