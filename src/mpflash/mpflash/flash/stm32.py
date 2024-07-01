"""Flash STM32 boards using pydfu"""

from pathlib import Path

from loguru import logger as log

from mpflash.mpremoteboard import MPRemoteBoard

# from .flash_stm32_cube import flash_stm32_cubecli
from .stm32_dfu import dfu_init, flash_stm32_dfu


def flash_stm32(mcu: MPRemoteBoard, fw_file: Path, *, erase: bool):
    # sourcery skip: lift-return-into-if
    dfu_init()
    if updated := flash_stm32_dfu(mcu, fw_file=fw_file, erase=erase):
        mcu.wait_for_restart()
        log.success(f"Flashed {mcu.version} to {mcu.board}")
    return updated
