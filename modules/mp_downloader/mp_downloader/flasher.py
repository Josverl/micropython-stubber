import os
import shutil
import subprocess
import time
import sys

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

from stubber.bulk.mpremoteboard import MPRemoteBoard

from .common import DEFAULT_FW_PATH, PORT_FWTYPES

# #########################################################################################################
FWInfo = Dict[str, Union[str, bool]]


def load_firmwares(fw_folder: Path) -> List[FWInfo]:
    """Load a list of available  firmwares from the jsonl file"""
    firmwares: List[FWInfo] = []
    with jsonlines.open(fw_folder / "firmware.jsonl") as reader:
        firmwares.extend(iter(reader))
    # sort by filename
    firmwares.sort(key=lambda x: x["filename"])
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
        # ESP board naming conventions have changed by adding a PORT refix 
        if port.startswith("esp") and not board_id.startswith(port.upper()):
            board_id = f"{port.upper()}_{board_id}"
        # RP2 board naming conventions have changed by adding a _RPIprefix 
        if port == "rp2" and not board_id.startswith("RPI_"):
            board_id = f"RPI_{board_id}"

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
    # sort by filename
    fw_list.sort(key=lambda x: x["filename"])
    return fw_list


# #########################################################################################################
# Flash SAMD and RP2 via UF2
# #########################################################################################################
class UF2Disk:
    """Info to support mounting and unmounting of UF2 drives on linux"""
    device_path: str
    label: str
    mountpoint: str

    def __repr__(self):
        return repr(self.__dict__)

def get_uf2_drives():
    """
    Get a list of all the (un)mounted UF2 drives
    """
    if sys.platform != "linux":
        log.error("pumount only works on Linux")
        return
    # import blkinfo only on linux
    from blkinfo import BlkDiskInfo

    myblkd = BlkDiskInfo()
    filters = {
    'tran': 'usb',
    }
    usb_disks = myblkd.get_disks(filters)
    for disk in usb_disks:
        if disk["fstype"] == "vfat":
            uf2_part = disk
            # unpartioned usb disk or partition (e.g. /dev/sdb )
            # SEEED WIO Terminal is unpartioned
            # print( json.dumps(uf2_part, indent=4))
            uf2 = UF2Disk()
            uf2.device_path = "/dev/" + uf2_part["name"]
            uf2.label = uf2_part["label"]
            uf2.mountpoint = uf2_part["mountpoint"]
            yield uf2 
        elif disk["type"] == "disk" and disk.get("children") and len(disk.get("children")) > 0:
            if disk.get("children")[0]["type"] == "part" and disk.get("children")[0]["fstype"] == "vfat":
                uf2_part = disk.get("children")[0]
                # print( json.dumps(uf2_part, indent=4))
                uf2 = UF2Disk()
                uf2.device_path = "/dev/" + uf2_part["name"]
                uf2.label = uf2_part["label"]
                uf2.mountpoint = uf2_part["mountpoint"]
                yield uf2

dismount_me : List[UF2Disk] = []

def pmount(disk: UF2Disk):
    """
    Mount a UF2 drive if there is no mountpoint yet.
    """
    global dismount_me
    if not disk.mountpoint:
        if not disk.label:
            disk.label = "UF2BOOT"
        disk.mountpoint = f"/media/{disk.label}"
        subprocess.run(["pmount",disk.device_path,  disk.mountpoint ])
        log.info(f"Mounted {disk.label} at {disk.mountpoint}")
        dismount_me.append(disk)
    else:
        log.warning(f"{disk.label} already mounted at {disk.mountpoint}")

def pumount(disk: UF2Disk):
    """
    Unmount a UF2 drive
    """
    if sys.platform != "linux":
        log.error("pumount only works on Linux")
        return
    if disk.mountpoint:
        subprocess.run(["pumount", disk.mountpoint]) # ), f"/media/{disk.label}"])
        log.info(f"Unmounted {disk.label} from {disk.mountpoint}")
        disk.mountpoint = f""
    else:
        log.warning(f"{disk.label} already dismounted")

def dismount_uf2():
    global dismount_me
    for disk in dismount_me:
        pumount(disk)
    dismount_me = []

def flash_uf2(mcu: MPRemoteBoard, fw_file: Path) -> Optional[MPRemoteBoard]:
    """
    Flash .UF2 devices via bootloader and filecopy
    - mpremote bootloader
    - Wait for the device to mount as a drive (up to 5s)
    - detect new drive with INFO_UF2.TXT
    - copy the firmware file to the drive
    - wait for the device to restart (5s)

    for Lunix : 
    pmount and pumount are used to mount and unmount the drive
    as this is not done automatically by the OS in headless mode.
    """
    if PORT_FWTYPES[mcu.port] not in [".uf2"]:
        log.error(f"UF2 not supported on {mcu.board} on {mcu.serialport}")
        return None

    log.info(f"Entering UF2 bootloader on {mcu.board} on {mcu.serialport}")
    mcu.run_command("bootloader", timeout=10)

    if sys.platform == "linux":
        destination = wait_for_UF2_linux()
    elif sys.platform == "win32":
        destination = wait_for_UF2_windows()
    else:
        log.error(f"OS {sys.platform} not supported")
        return None

    if not destination or not destination.exists() or not (destination / "INFO_UF2.TXT").exists():
        log.error("Board is not in bootloader mode")
        return None

    log.info("Board is in bootloader mode")
    log.info(f"Copying {fw_file} to {destination}")
    shutil.copy(fw_file, destination)
    log.success("Done copying, resetting the board and wait for it to restart")
    if sys.platform == "linux":
        dismount_uf2()
    time.sleep(5 * 2) # 5 secs to short on linux
    return mcu

def wait_for_UF2_linux():
    destination = ""
    wait = 10
    uf2_drives = []
    while not destination and wait > 0:
        log.info(f"Waiting for mcu to mount as a drive : {wait} seconds left")
        uf2_drives += list(get_uf2_drives())
        for drive in get_uf2_drives():
            pmount(drive)
            time.sleep(1)
            if Path(drive.mountpoint, "INFO_UF2.TXT").exists():
                # board_id = get_board_id(Path(drive.mountpoint))
                destination = Path(drive.mountpoint)
                break
        time.sleep(1)
        wait -= 1
    return destination

def wait_for_UF2_windows():
    destination = ""
    wait = 10
    while not destination and wait > 0:
        log.info(f"Waiting for mcu to mount as a drive : {wait} seconds left")
        drives = [drive.device for drive in psutil.disk_partitions()]
        for drive in drives:
            if Path(drive, "INFO_UF2.TXT").exists():
                board_id = get_board_id(Path(drive))
                destination = Path(drive)
                break
        time.sleep(1)
        wait -= 1
    return destination

def get_board_id(path:Path):
    # Option : read Board-ID from INFO_UF2.TXT
    board_id = "Unknown"
    with open(path /  "INFO_UF2.TXT") as f:
        data = f.readlines()
    for line in data:
        if line.startswith("Board-ID"):
            board_id = line[9:].strip()
    log.trace(f"Found Board-ID={board_id}")
    return board_id


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
        # baud_rate = str(115_200)
    cmds: List[List[str]] = []
    if erase_flash:
        cmds.append(f"esptool --chip {mcu.cpu} --port {mcu.serialport} erase_flash".split())

    if mcu.cpu.upper() in ("ESP32", "ESP32S2"):
        start_addr = "0x1000"
    elif mcu.cpu.upper() in ("ESP32S3", "ESP32C3"):
        start_addr = "0x0"
    if mcu.cpu.upper().startswith("ESP32"):
        cmds.append(
            f"esptool --chip {mcu.cpu} --port {mcu.serialport} -b {baud_rate} write_flash --compress {start_addr}".split()
            + [str(fw_file)]
        )
    elif mcu.cpu.upper() == "ESP8266":
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
            log.debug(f"Multiple firmwares found for {mcu.board} on {mcu.serialport} with version {target_version}")
        # just use the last firmware
        fw_info = board_firmwares[-1]
        log.info(f"Found firmware {fw_info['filename']} for {mcu.board} on {mcu.serialport} with version {target_version}")
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
    "--serial",
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
        mcu.cpu = port if port.startswith("esp") else ""
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
        # use the most recent matching firmware  
        todo = [(mcu, firmwares[-1])]
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
