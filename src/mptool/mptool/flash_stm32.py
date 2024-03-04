"""
Flash STM32 using STM32CubeProgrammer
needs to be installed independenty from https://www.st.com/en/development-tools/stm32cubeprog.html

On Linux needs to be run with sudo - because ?
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import bincopy
from loguru import logger as log
from strip_ansi import strip_ansi

from stubber.bulk.mpremoteboard import MPRemoteBoard

STM32_CLI_WIN = "C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin\\STM32_Programmer_CLI.exe"
STM32_CLI_LINUX = "/home/jos/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/STM32_Programmer_CLI"


def get_stm32_start_address(fw_file: Path):
    """
    Get the start address of the firmware file, to allow automatic restart from that address after flashing
    """
    try:
        fw_hex = bincopy.BinFile(str(fw_file))
        return f"0x{fw_hex.execution_start_address:08X}"
    except Exception:

        return ""


def flash_stm32(
    mcu: MPRemoteBoard, fw_file: Path, *, erase: bool = True
) -> Optional[MPRemoteBoard]:
    """
    Flash STM32 devices using STM32CubeProgrammer CLI
    - Enter bootloader mode
    - wait 2s for the device to be detected
    - list the connected DFU devices

    Windows only for now
    """
    if sys.platform == "linux":
        STM32_CLI = STM32_CLI_LINUX
    elif sys.platform == "win32":
        STM32_CLI = STM32_CLI_WIN
    else:
        log.error(f"OS {sys.platform} not supported")
        return None

    if not Path(STM32_CLI).exists():
        log.error(
            f"STM32CubeProgrammer not found at {STM32_CLI}\nPlease install it from https://www.st.com/en/development-tools/stm32cubeprog.html"
        )
        return None

    log.info(f"Entering STM bootloader on {mcu.board} on {mcu.serialport}")
    mcu.run_command("bootloader")
    time.sleep(2)
    # run STM32_Programmer_CLI.exe --list
    cmd = [
        STM32_CLI,
        "--list",
    ]
    results = subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()
    results = [strip_ansi(line) for line in results]
    if not any(["Product ID             : STM32  BOOTLOADER" in l for l in results]):
        log.error("No STM32 BOOTLOADER detected")
        return None
    echo = False
    for line in results:
        if line.startswith("=====  DFU Interface"):
            echo = True
        if line.startswith("===== STLink"):
            echo = False
        if echo:
            print(line)
    # Try to connect - no action
    cmd = [
        STM32_CLI,
        "--connect",
        "port=USB1",
    ]
    results = subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()
    if erase:
        log.info("Erasing flash")
        cmd = [
            STM32_CLI,
            "--connect",
            "port=USB1",
            "--erase",
            "all",
        ]
        results = subprocess.run(
            cmd, capture_output=True, text=True
        ).stdout.splitlines()
        results = [strip_ansi(line) for line in results]
    log.info("Flashing")
    start_address = get_stm32_start_address(fw_file)

    log.trace(
        f"STM32_Programmer_CLI --connect port=USB1 --write {str(fw_file)} --go {start_address}"
    )
    cmd = [
        STM32_CLI,
        "--connect",
        "port=USB1",
        "--write",
        str(fw_file),
        "--go",
        start_address,
    ]
    results = subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()
    log.success("Done flashing, resetting the board and wait for it to restart")
    time.sleep(5)
    mcu.get_mcu_info()
    return mcu
