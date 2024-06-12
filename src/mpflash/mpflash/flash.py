from pathlib import Path

from loguru import logger as log

from mpflash.bootloader import enter_bootloader
from mpflash.common import PORT_FWTYPES

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
        fw_file = fw_folder / fw_info.filename
        if not fw_file.exists():
            log.error(f"File {fw_file} does not exist, skipping {mcu.board} on {mcu.serialport}")
            continue
        log.info(f"Updating {mcu.board} on {mcu.serialport} to {fw_info.version}")
        updated = None
        # try:
        if mcu.port in [port for port, exts in PORT_FWTYPES.items() if ".uf2" in exts] and fw_file.suffix == ".uf2":
            # any .uf2 port ["samd", "rp2", "nrf"]:
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
    return flashed
