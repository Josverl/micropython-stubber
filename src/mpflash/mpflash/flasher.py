from pathlib import Path
from typing import List, Optional, Tuple

import jsonlines
import rich_click as click
from loguru import logger as log

# TODO: - refactor so that we do not need the entire stubber package
from stubber.bulk.mpremoteboard import MPRemoteBoard

from .cli_group import cli
from .common import DEFAULT_FW_PATH, FWInfo, clean_version
from .config import config
from .flash_esp import flash_esp
from .flash_stm32 import flash_stm32
from .flash_uf2 import flash_uf2
from .list import show_mcus

# #########################################################################################################


def load_firmwares(fw_folder: Path) -> List[FWInfo]:
    """Load a list of available  firmwares from the jsonl file"""
    firmwares: List[FWInfo] = []
    try:
        with jsonlines.open(fw_folder / "firmware.jsonl") as reader:
            firmwares.extend(iter(reader))
    except FileNotFoundError:
        log.error(f"No firmware.jsonl found in {fw_folder}")
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
        log.error(f"No firmware files found. Please download the firmware first.")
        return []
    # filter by version
    version = clean_version(version, drop_v=True)
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
#
# #########################################################################################################
WorkList = List[Tuple[MPRemoteBoard, FWInfo]]


def auto_update(conn_boards: List[MPRemoteBoard], target_version: str, fw_folder: Path):
    """Builds a list of boards to update based on the connected boards and the firmware available"""
    wl: WorkList = []
    for mcu in conn_boards:
        if mcu.family != "micropython":
            log.warning(
                f"Skipping {mcu.family} {mcu.port} {mcu.board} on {mcu.serialport} as it is a MicroPython firmware"
            )
            continue
        board_firmwares = find_firmware(
            fw_folder=fw_folder,
            board=mcu.board,
            version=target_version,
            port=mcu.port,
            preview="preview" in target_version,
        )

        if not board_firmwares:
            log.error(f"No {target_version} firmware found for {mcu.board} on {mcu.serialport}.")
            continue
        if len(board_firmwares) > 1:
            log.debug(f"Multiple {target_version} firmwares found for {mcu.board} on {mcu.serialport}.")
        # just use the last firmware
        fw_info = board_firmwares[-1]
        log.info(f"Found {target_version} firmware {fw_info['filename']} for {mcu.board} on {mcu.serialport}.")
        wl.append((mcu, fw_info))
    return wl


# #########################################################################################################
# CLI
# #########################################################################################################


@cli.command(
    "flash",
    short_help="Flash one or all connected MicroPython boards with a specific firmware and version.",
)
@click.option(
    "--firmware",
    "-f",
    "fw_folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=DEFAULT_FW_PATH,
    show_default=True,
    help="The folder to retrieve the firmware from.",
)
@click.option(
    "--version",
    "-v",
    "target_version",
    default="stable",
    show_default=True,
    help="The version of MicroPython to flash.",
    metavar="SEMVER, stable or preview",
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
    help="The MicroPython board ID to flash. If not specified will try to read the BOARD_ID from the connected MCU.",
    metavar="BOARD_ID",
    default="",
)
@click.option(
    "--cpu",
    "--chip",
    "-c",
    "cpu",
    help="The CPU type to flash. If not specified will try to read the CPU from the connected MCU.",
    metavar="CPU",
)
@click.option(
    "--variant",
    help="The variant of the board to flash. If not specified will try to read the VARIANT from the connected MCU.",
    metavar="VARIANT",
    default="",
)
@click.option(
    "--erase/--no-erase",
    default=True,
    show_default=True,
    help="""Erase flash before writing new firmware. (not on UF2 boards)""",
)
@click.option(
    "--preview/--no-preview",
    default=False,
    show_default=True,
    help="""Include preview versions in the download list.""",
)
def cli_flash_board(
    target_version: str,
    fw_folder: Path,
    serial_port: Optional[str] = None,
    board: Optional[str] = None,
    port: Optional[str] = None,
    variant: Optional[str] = None,
    cpu: Optional[str] = None,
    erase: bool = False,
    preview: bool = False,
):
    todo: WorkList = []
    target_version = clean_version(target_version)
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
            preview=preview or "preview" in target_version,
        )
        if not firmwares:
            log.error(f"No firmware found for {port} {board} version {target_version}")
            return
        # use the most recent matching firmware
        todo = [(mcu, firmwares[-1])]
    elif serial_port:
        if serial_port == "auto":
            # update all connected boards
            conn_boards = [
                MPRemoteBoard(sp) for sp in MPRemoteBoard.connected_boards() if sp not in config.ignore_ports
            ]
        else:
            # just this serial port
            conn_boards = [MPRemoteBoard(serial_port)]
        show_mcus(conn_boards)
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
            updated = flash_uf2(mcu, fw_file=fw_file, erase=erase)
        elif mcu.port in ["esp32", "esp8266"]:
            updated = flash_esp(mcu, fw_file=fw_file, erase=erase)
        elif mcu.port in ["stm32"]:
            updated = flash_stm32(mcu, fw_file=fw_file, erase=erase)

        if updated:
            flashed.append(updated)
        else:
            log.error(f"Failed to flash {mcu.board} on {mcu.serialport}")

    if flashed:
        log.info(f"Flashed {len(flashed)} boards")
        # conn_boards = [
        #     MPRemoteBoard(sp)
        #     for sp in MPRemoteBoard.connected_boards()
        #     if sp not in config.ignore_ports
        # ]

        show_mcus(flashed, title="Connected boards after flashing")


# TODO:
# flash from some sort of queue to allow different images to be flashed to the same board
#  - flash variant 1
#  - stub variant 1
#  - flash variant 2
#  - stub variant 2
#
# JIT download / download any missing firmwares based on the detected boards
