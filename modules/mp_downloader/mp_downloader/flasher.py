import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import bincopy
import esptool
import jsonlines
import psutil
import rich_click as click
from loguru import logger as log
from rich import print
from rich.table import Table
from tenacity import RetryError

from stubber.bulk.mpremoteboard import MPRemoteBoard

from .common import DEFAULT_FW_PATH, PORT_FWTYPES

# #########################################################################################################
FWInfo = Dict[str, Union[str, bool]]


def load_firmwares(fw_folder: Path) -> List[FWInfo]:
    """Load a list of available  firmwares from the jsonl file"""
    firmwares: List[FWInfo] = []
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
    trie: int = 1,
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

    if not fw_list and trie < 2:
        board_id = board.replace("_", "-")
        # ESP board naming conventions have changed by addin a prefix ( port / CPU)
        if port.startswith("esp") and not board_id.startswith(port.upper()):
            board_id = f"{port.upper()}_{board_id}"

        log.warning(f"Trying to find a firmware for the board {board_id}")
        fw_list = find_firmware(
            fw_folder=fw_folder,
            board=board_id,
            version=version,
            port=port,
            preview=preview,
            trie=trie + 1,
        )
        # hope we have a match now for the board
    return fw_list


# #########################################################################################################
# Flash SAMD and RP2 via UF2
# #########################################################################################################


def flash_uf2(mcu: MPRemoteBoard, fw_file: Path) -> Optional[MPRemoteBoard]:
    """
    Flash .UF2 devices via bootloader and filecopy
    - Enter bootloader mode
    - Wait for the device to mount as a drive (up to 5s)
    - copy the firmware file to the drive
    - wait for the device to restart (5s)
    """
    if PORT_FWTYPES[mcu.port] not in [".uf2"]:
        log.error(f"UF2 not supported on {mcu.board} on {mcu.serialport}")
        return None

    log.info(f"Entering UF2 bootloader on {mcu.board} on {mcu.serialport}")
    mcu.run_command("bootloader")

    destination = ""
    wait = 5
    while not destination and wait > 0:
        log.info(f"Waiting for mcu to mount as a drive : {wait} seconds left")
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
                log.trace(f"Found Board-ID={board_id}")
                destination = drive
                break
        time.sleep(1)
        wait -= 1
    if not destination or not Path(destination).exists() or not Path(destination, "INFO_UF2.TXT").exists():
        log.error("Board is not in bootloader mode")
        return None

    log.info("Board is in bootloader mode")
    log.info(f"Copying {fw_file} to {destination}")
    shutil.copy(fw_file, destination)
    log.success("Done copying, resetting the board and wait for it to restart")
    time.sleep(5)
    # refresh bord info
    # try:
    #     # sometimes a board might not re-appear as the same com port
    #     mcu.get_mcu_info()
    # except (Exception, RetryError, RuntimeError) as e:
    #     log.error(f"Failed to get mcu info {e}")
    return mcu


# #########################################################################################################
# Flash ESP32 and ESP8266 via esptool
# #########################################################################################################


def flash_esp(mcu: MPRemoteBoard, fw_file: Path, *, erase_flash: bool = True) -> Optional[MPRemoteBoard]:
    if mcu.port not in ["esp32", "esp8266"] or mcu.board in ["ARDUINO_NANO_ESP32"]:
        log.error(f"esptool not supported for {mcu.port} {mcu.board} on {mcu.serialport}")
        return None

    log.info(f"Flashing {fw_file} on {mcu.board} on {mcu.serialport}")
    if mcu.port == "esp8266":
        baud_rate = str(460_800)
    else:
        baud_rate = str(512_000)
    cmds: List[List[str]] = []
    if erase_flash:
        cmds.append(f"esptool --chip {mcu.cpu} --port {mcu.serialport} erase_flash".split())

    if mcu.cpu.upper() == ("ESP32", "ESP32S2"):
        start_addr = "0x1000"
    elif mcu.cpu.upper() in ("ESP32S3", "ESP32C3"):
        start_addr = "0x0"
    if mcu.cpu.upper().startswith("ESP32"):
        cmds.append(
            f"esptool --chip {mcu.cpu} --port {mcu.serialport} -b {baud_rate} write_flash -z {start_addr}".split()
            + [str(fw_file)]
        )
    elif mcu.cpu.upper() == "ESP8266":
        start_addr = "0x0"
        cmds.append(
            f"esptool --chip {mcu.cpu} --port {mcu.serialport} -b {baud_rate} write_flash --flash_size=detect {start_addr}".split()
            + [str(fw_file)]
        )

    for cmd in cmds:
        log.info(f"Running {' '.join(cmd)} ")
        esptool.main(cmd[1:])

    log.info("Done flashing, resetting the board and wait for it to restart")
    time.sleep(5)
    mcu.get_mcu_info()
    log.success(f"Flashed {mcu.version} to {mcu.board} on {mcu.serialport} done")
    return mcu


# #########################################################################################################
# flash STM32 using STM32CubeProgrammer
# needs to be installed independenty from https://www.st.com/en/development-tools/stm32cubeprog.html
# #########################################################################################################


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
    """
    Flash STM32 devices using STM32CubeProgrammer CLI
    - Enter bootloader mode
    - wait 2s for the device to be detected
    - list the connected DFU devices
    """
    STM32_CLI = "C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin\\STM32_Programmer_CLI.exe"

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
    if "Product ID             : STM32  BOOTLOADER" in results:
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
    if erase_flash:
        log.info("Erasing flash")
        cmd = [
            STM32_CLI,
            "--connect",
            "port=USB1",
            "--erase",
            "all",
        ]
        results = subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()

    log.info("Flashing")
    start_address = get_stm32_start_address(fw_file)

    log.trace(f"STM32_Programmer_CLI.exe --connect port=USB1 --write {str(fw_file)} --go {start_address}")
    # !"C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe" --connect port=USB1 --write "{str(fw_file)}" --go {start_address}
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


# #########################################################################################################
#
# #########################################################################################################
WorkList = List[Tuple[MPRemoteBoard, FWInfo]]


def auto_update(conn_boards: List[MPRemoteBoard], target_version: str, fw_folder: Path):
    """Builds a list of boards to update based on the connected boards and the firmware available"""
    wl: WorkList = []
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
            log.error(f"No firmware found for {mcu.board}? on {mcu.serialport} with version {target_version}")
            continue
        if len(board_firmwares) > 1:
            log.warning(f"Multiple firmwares found for {mcu.board} on {mcu.serialport} with version {target_version}")

        # just use the first firmware
        fw_info = board_firmwares[0]
        wl.append((mcu, fw_info))
    return wl


# #########################################################################################################
# CLI
# #########################################################################################################
@click.group()
def cli():
    pass


@cli.command("list")
def show_list():
    conn_boards = [MPRemoteBoard(p) for p in MPRemoteBoard.connected_boards()]
    show_boards(conn_boards)


@cli.command()
@click.option(
    "--firmware",
    "-f",
    "fw_folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default="./firmware",
    show_default=True,
    help="The folder to retrieve the firmware from.",
)
@click.option(
    "--version",
    "-v",
    "target_version",
    default="preview",
    show_default=True,
    help="The version of MicroPython to flash.",
    metavar="SEMVER or preview",
)
@click.option(
    "--serial-port",
    "-s",
    "serial_port",
    default="auto",
    show_default=True,
    help="Which serial port(s) to flash",
    metavar="SERIAL_PORT",
)
@click.option(
    "--port",
    "-p",
    "port",
    help="The MicroPython port to flash",
    metavar="PORT",
    default="",
)
@click.option(
    "--board",
    "-b",
    "board",
    help="The MicroPython board ID to flash",
    metavar="BOARD_ID",
    default="",
)
@click.option(
    "--erase/--no-erase",
    default=True,
    show_default=True,
    help="""Erase flash before writing new firmware.""",
)
def update(
    target_version: str,
    fw_folder: Path,
    serial_port: Optional[str] = None,
    board: Optional[str] = None,
    port: Optional[str] = None,
    variant: Optional[str] = None,
    erase: bool = False,
):
    todo: WorkList = []
    # Update all micropython boards to the latest version
    if target_version and port and board and serial_port:
        mcu = MPRemoteBoard(serial_port)
        mcu.port = port
        mcu.board = board
        firmwares = find_firmware(
            fw_folder=fw_folder,
            board=board,
            version=target_version,
            port=port,
            preview="preview" in target_version,
        )
        if not firmwares:
            log.error(f"No firmware found for {port} {board} version {target_version}")
            return
        todo = [(mcu, firmwares[0])]
    elif serial_port:
        if serial_port == "auto":
            # update all connected boards
            conn_boards = [MPRemoteBoard(p) for p in MPRemoteBoard.connected_boards()]
        else:
            # just this serial port
            conn_boards = [MPRemoteBoard(serial_port)]
        show_boards(conn_boards)
        todo = auto_update(conn_boards, target_version, fw_folder)

    flashed = []
    for mcu, fw_info in todo:
        fw_file = fw_folder / fw_info["filename"]  # type: ignore
        if not fw_file.exists():
            log.error(f"File {fw_file} does not exist, skipping {mcu.board} on {mcu.serialport}")
            continue
        log.info(f"Updating {mcu.board} on {mcu.serialport} to {fw_info['version']}")

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

    conn_boards = [MPRemoteBoard(p) for p in MPRemoteBoard.connected_boards()]
    show_boards(conn_boards, title="Connected boards after flashing")


def show_boards(conn_boards: List[MPRemoteBoard], title: str = "Connected boards"):
    table = Table(title=title)
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
#   -specify port / bord / version to flash
# flash from some sort of queue to allow different images to be flashed to the same board
#  - flash variant 1
#  - stub variant 1
#  - flash variant 2
#  - stub variant 2
#
# JIT download / download any missing firmwares based on the detected boards


if __name__ == "__main__":
    cli()
