"""
# #########################################################################################################
# Flash ESP32 and ESP8266 via esptool
# #########################################################################################################
"""

from pathlib import Path
from typing import List, Optional

import esptool
from loguru import logger as log

from mpflash.mpboard_id import find_known_board
from mpflash.mpremoteboard import MPRemoteBoard


def flash_esp(mcu: MPRemoteBoard, fw_file: Path, *, erase: bool = True) -> Optional[MPRemoteBoard]:
    if mcu.port not in ["esp32", "esp8266"] or mcu.board in ["ARDUINO_NANO_ESP32"]:
        log.error(f"esptool not supported for {mcu.port} {mcu.board} on {mcu.serialport}")
        return None

    log.info(f"Flashing {fw_file} on {mcu.board} on {mcu.serialport}")
    if not mcu.cpu:
        # Lookup CPU based on the board name
        mcu.cpu = find_known_board(mcu.board).cpu

    cmds: List[List[str]] = []
    if erase:
        cmds.append(f"esptool --chip {mcu.cpu} --port {mcu.serialport} erase_flash".split())

    if mcu.cpu.upper().startswith("ESP32"):
        baud_rate = str(921_600)
        if mcu.cpu.upper() in ("ESP32", "ESP32S2"):
            start_addr = "0x1000"
        elif mcu.cpu.upper() in ("ESP32S3", "ESP32C3"):
            start_addr = "0x0"
        cmds.append(
            f"esptool --chip {mcu.cpu} --port {mcu.serialport} -b {baud_rate} write_flash --compress {start_addr}".split()
            + [str(fw_file)]
        )
    elif mcu.cpu.upper() == "ESP8266":
        baud_rate = str(460_800)
        start_addr = "0x0"
        cmds.append(
            f"esptool --chip {mcu.cpu} --port {mcu.serialport} -b {baud_rate} write_flash --flash_size=detect {start_addr}".split()
            + [str(fw_file)]
        )
    try:
        for cmd in cmds:
            log.info(f"Running {' '.join(cmd)} ")
            esptool.main(cmd[1:])
    except Exception as e:
        log.error(f"Failed to flash {mcu.board} on {mcu.serialport} : {e}")
        return None

    log.info("Done flashing, resetting the board...")
    mcu.wait_for_restart()
    log.success(f"Flashed {mcu.serialport} to {mcu.board} {mcu.version}")
    return mcu
