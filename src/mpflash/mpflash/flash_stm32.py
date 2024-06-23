"""Flash STM32 boards using either STM32CubeProgrammer CLI or dfu-util"""

from pathlib import Path

from loguru import logger as log

# from .flash_stm32_cube import flash_stm32_cubecli
from .flash_stm32_dfu import dfu_init, flash_stm32_dfu
from mpflash.mpremoteboard import MPRemoteBoard


def flash_stm32(mcu: MPRemoteBoard, fw_file: Path, *, erase: bool, stm32_dfu: bool = True):
    # sourcery skip: lift-return-into-if
    dfu_init()
    updated = flash_stm32_dfu(mcu, fw_file=fw_file, erase=erase)
    # if stm32_dfu:
    # else:
    #     log.info("Using STM32CubeProgrammer CLI")
    #     updated = flash_stm32_cubecli(mcu, fw_file=fw_file, erase=erase)

    mcu.wait_for_restart()
    log.success(f"Flashed {mcu.version} to {mcu.board}")
    return updated
