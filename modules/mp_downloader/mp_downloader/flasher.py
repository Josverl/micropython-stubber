import shutil
import time
from pathlib import Path
from typing import List, Optional

import jsonlines
import psutil
from loguru import logger as log
from rich import print
from rich.table import Table

from stubber.bulk.mpremoteboard import MPRemoteBoard

from .common import DEFAULT_FW_PATH, PORT_FWTYPES


def load_firmwares(fw_folder: Path):
    """Load a list of available  firmwares from the jsonl file"""
    firmwares = []
    with jsonlines.open(fw_folder / "firmware.jsonl") as reader:
        firmwares.extend(iter(reader))
    return firmwares


def find_firmware(
    *,
    board: str,
    version: str = "",
    port: str = "",
    preview: bool = False,
    variants: bool = False,
    fw_folder: Optional[Path] = None,
):
    # TODO : better path handling
    fw_folder = fw_folder or DEFAULT_FW_PATH
    # Use the information in firmwares.jsonl to find the firmware file
    fw_list = load_firmwares(fw_folder)

    if not fw_list:
        raise FileNotFoundError(f"No firmware files found in {fw_folder}")
    # filter by version
    if preview or "preview" in version:
        # never get a preview for an older version
        fw_list = [fw for fw in fw_list if fw["preview"]]
    else:
        fw_list = [fw for fw in fw_list if fw["version"] == version]

    # filter by port
    if port:
        fw_list = [fw for fw in fw_list if fw["port"] == port]

    if board:
        if variants:
            fw_list = [fw for fw in fw_list if fw["board"] == board]
        else:
            # the variant should match exactly the board name
            fw_list = [fw for fw in fw_list if fw["variant"] == board]

    if not fw_list:
        print(f"No firmware files found for {version}")
        return []

    return fw_list


def flash_uf2(mcu: MPRemoteBoard, fw_file: Path) -> Optional[MPRemoteBoard]:
    """
    Flash .UF2 devices via bootloader and filecopy
    - Enter bootloader mode
    - Wait for the device to mount as a drive (up to 5s)
    - copy the firmware file to the drive
    - wait for the device to restart (5s)
    """
    if PORT_FWTYPES[mcu.port] not in [".uf2"]:
        print(f"UF2 not supported on {mcu.board} on {mcu.serialport}")
        return None

    print(f"Entering UF2 bootloader on {mcu.board} on {mcu.serialport}")
    mcu.run_command("bootloader")

    destination = ""
    wait = 5
    while not destination and wait > 0:
        print(f"Waiting for mcu to mount as a drive : {wait} seconds left")
        drives = [drive.device for drive in psutil.disk_partitions()]
        for drive in drives:
            if Path(drive, "INFO_UF2.TXT").exists():
                # Option : read Board-ID from INFO_UF2.TXT
                board_id = "Unknown"
                with open(Path(drive, "INFO_UF2.TXT")) as f:
                    data = f.readlines()
                for line in data:
                    if line.startswith("Board-ID="):
                        board_id = line.split("=")[1].strip()
                print(f"Found Board-ID={board_id}")
                destination = drive
                break
        time.sleep(1)
        wait -= 1
    if not destination or not Path(destination).exists() or not Path(destination, "INFO_UF2.TXT").exists():
        print("Board is not in bootloader mode")
        return None

    print("Board is in bootloader mode")
    print(f"Copying {fw_file} to {destination}")
    shutil.copy(fw_file, destination)
    print("Done copying, resetting the board and wait for it to restart")
    time.sleep(5)
    # refresh bord info
    mcu.get_mcu_info()
    return mcu


# Flash ESP32 and ESP8266 via esptool
# TODO : use sys.executable to run esptool to avoid getting a wrong version


def flash_esp(mcu: MPRemoteBoard, fw_file: Path, *, erase_flash: bool = True) -> Optional[MPRemoteBoard]:
    if mcu.port not in ["esp32", "esp8266"] or mcu.board in ["ARDUINO_NANO_ESP32"]:
        print(f"esptool not supported for {mcu.port} {mcu.board} on {mcu.serialport}")
        return None

    log.info(f"Flashing {fw_file} on {mcu.board} on {mcu.serialport}")
    if mcu.port == "esp8266":
        baud_rate = str(460_800)
    else:
        baud_rate = str(512_000)
    cmds: List[str] = []
    if erase_flash:
        cmds.append(f"esptool --chip {mcu.cpu} --port {mcu.serialport} erase_flash")

    if mcu.cpu.upper() == ("ESP32", "ESP32S2"):
        start_addr = "0x1000"
    elif mcu.cpu.upper() in ("ESP32S3", "ESP32C3"):
        start_addr = "0x0"
    if mcu.cpu.startswith("esp32"):
        cmds.append(
            f"esptool --chip {mcu.cpu} --port {mcu.serialport} -b {baud_rate} write_flash -z {start_addr} {fw_file}"
        )
    elif mcu.cpu.upper() == "ESP8266":
        start_addr = "0x0"
        cmds.append(
            f"esptool --chip {mcu.cpu} --port {mcu.serialport} -b {baud_rate} write_flash --flash_size=detect {start_addr} {fw_file}"
        )

    for cmd in cmds:
        log.info(f"Running {cmd}")
        # TODO : check for errors
        subprocess.run(cmd, capture_output=False, text=True)

    print("Done flashing, resetting the board and wait for it to restart")
    time.sleep(5)
    mcu.get_mcu_info()
    log.success(f"Flashed {mcu.version} to {mcu.board} on {mcu.serialport} done")
    return mcu


# # flash STM32 using STM32CubeProgrammer
import subprocess

import bincopy


def get_stm32_start_address(fw_file: Path):
    """
    Get the start address of the firmware file, to allow automatic restart from that address after flashing
    """
    try:
        fw_hex = bincopy.BinFile(str(fw_file))
        return f"0x{fw_hex.execution_start_address:08X}"
    except Exception:
        return ""


def flash_stm32(mcu: MPRemoteBoard, fw_file: Path, *, erase_flash: bool = True) -> Optional[MPRemoteBoard]:
    print(f"Entering STM bootloader on {mcu.board} on {mcu.serialport}")
    # %mpy --select {mcu.serialport}
    # %mpy --bootloader # TODO: add this to micropython-magic

    time.sleep(2)
    # run STM32_Programmer_CLI.exe --list
    cmd = [
        "C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin\\STM32_Programmer_CLI.exe",
        "--list",
    ]
    results = subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()
    if "Product ID             : STM32  BOOTLOADER" in results:
        print("No STM32 BOOTLOADER detected")
        return None
    echo = False
    for line in results:
        if line.startswith("=====  DFU Interface"):
            echo = True
        if line.startswith("===== STLink"):
            echo = False
        if echo:
            print(line)

    #  !"C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe" --connect port=USB1
    cmd = [
        "C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin\\STM32_Programmer_CLI.exe",
        "--connect",
        "port=USB1",
    ]
    results = subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()
    if erase_flash:
        print("Erasing flash")
        # !"C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe" --connect port=USB1 --erase all
        cmd = [
            "C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin\\STM32_Programmer_CLI.exe",
            "--connect",
            "port=USB1",
            "--erase",
            "all",
        ]
        results = subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()

    print("Flashing")
    start_address = get_stm32_start_address(fw_file)

    print(f"STM32_Programmer_CLI.exe --connect port=USB1 --write {str(fw_file)} --go {start_address}")
    # !"C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe" --connect port=USB1 --write "{str(fw_file)}" --go {start_address}
    cmd = [
        "C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin\\STM32_Programmer_CLI.exe",
        "--connect",
        "port=USB1",
        "--write",
        str(fw_file),
        "--go",
        start_address,
    ]
    results = subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()
    print("Done flashing, resetting the board and wait for it to restart")
    time.sleep(5)
    mcu.get_mcu_info()
    return mcu


def cli(target_version: str = "preview"):
    conn_boards = [MPRemoteBoard(p) for p in MPRemoteBoard.connected_boards()]
    show_connected(conn_boards)

    # Update all micropython boards to the latest version

    target_version = "1.22.1"
    target_version = "preview"
    updated = []
    fw_folder = Path("D:\\MyPython\\micropython-stubber") / "firmware"
    for mcu in conn_boards:
        if mcu.family != "micropython":
            log.warning(f"Skipping {mcu.board} on {mcu.serialport} as it is not a micropython board")
            continue
        board_firmwares = find_firmware(
            fw_folder=fw_folder,
            board=mcu.board,
            version=target_version,
            port=mcu.port,
            preview="preview" in target_version,
        )
        if not board_firmwares:
            log.warning(f"No firmware found for {mcu.board} on {mcu.serialport} with version {target_version}")
            board_id = mcu.board.replace("_", "-")
            # ESP board naming conventions have changed by addin a prefix ( port / CPU)
            if mcu.port.startswith("esp") and not board_id.startswith(mcu.port.upper()):
                board_id = f"{mcu.port.upper()}_{board_id}"

            log.warning(f"Trying to find a firmware for the board {board_id}")
            board_firmwares = find_firmware(
                fw_folder=fw_folder,
                board=board_id,
                version=target_version,
                port=mcu.port,
                preview="preview" in target_version,
            )
            # we have a match now for the board
        if not board_firmwares:
            log.warning(f"No firmware found for {board_id}? on {mcu.serialport} with version {target_version}")
            continue
        if len(board_firmwares) > 1:
            log.warning(f"Multiple firmwares found for {mcu.board} on {mcu.serialport} with version {target_version}")

        # just use the first firmware
        fw_info = board_firmwares[0]
        # the filename is relative to the firmware folder
        fw_file = fw_folder / fw_info["filename"]
        if not fw_file.exists():
            log.error(f"File {fw_file} does not exist, skipping {mcu.board} on {mcu.serialport}")
            continue
        log.info(f"Updating {mcu.board} on {mcu.serialport} to {fw_info['version']}")

        flashed = []
        updated = None
        # try:
        if mcu.port in ["samd", "rp2"]:
            updated = flash_uf2(mcu, fw_file=fw_file)
        elif mcu.port in ["esp32", "esp8266"]:
            updated = flash_esp(mcu, erase_flash=True, fw_file=fw_file)

        elif mcu.port in ["stm32"]:
            updated = flash_stm32(mcu, erase_flash=False, fw_file=fw_file)

        if updated:
            flashed.append(updated)
        else:
            log.error(f"Failed to flash {mcu.board} on {mcu.serialport}")


def show_connected(conn_boards: List[MPRemoteBoard]):
    table = Table(title="Connected boards")
    table.add_column("Serial")
    table.add_column("Family")
    table.add_column("Port")
    table.add_column("Board")
    table.add_column("CPU")
    table.add_column("Version")
    table.add_column("build")

    for mcu in conn_boards:
        mcu.get_mcu_info()
        table.add_row(mcu.serialport, mcu.family, mcu.port, mcu.board, mcu.cpu, mcu.version, mcu.build)
    print(table)


# TODO:
# add option to skip autodetect
# specify port / bord / version to flash
# flsh from some sort of queue to allow different images to be flashed to the same board
# flash variant 1
# stub variant 1
# flash variant 2
# stub variant 2


if __name__ == "__main__":
    cli()
