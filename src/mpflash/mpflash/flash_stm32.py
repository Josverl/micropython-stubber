"""Flash STM32 boards using either STM32CubeProgrammer CLI or dfu-util"""

from pathlib import Path
from .flash_stm32_dfu import flash_stm32_dfu
from .flash_stm32_cube import flash_stm32_cubecli

from .mpremoteboard.mpremoteboard import MPRemoteBoard


def flash_stm32(mcu: MPRemoteBoard, fw_file: Path, *, erase: bool, stm32_hex: bool):
    """Flash STM32 boards using either STM32CubeProgrammer CLI or dfu-util"""
    # TODO: Check installed utilities / Lazy import
    if stm32_hex:
        updated = flash_stm32_cubecli(mcu, fw_file=fw_file, erase=erase)
    else:
        updated = flash_stm32_dfu(mcu, fw_file=fw_file, erase=erase)
    return updated
