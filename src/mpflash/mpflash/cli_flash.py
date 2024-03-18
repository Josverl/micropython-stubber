from pathlib import Path
from typing import Optional

import rich_click as click
from loguru import logger as log

from mpflash.mpremoteboard import MPRemoteBoard

from .cli_group import cli
from .cli_list import show_mcus
from .common import clean_version
from .config import config
from .flash import WorkList, auto_update, enter_bootloader, find_firmware
from .flash_esp import flash_esp
from .flash_stm32 import flash_stm32
from .flash_uf2 import flash_uf2
from .common import FWInfo, PORT_FWTYPES

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
    default=config.firmware_folder,
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
    "--erase/--no-erase",
    default=True,
    show_default=True,
    help="""Erase flash before writing new firmware. (not on UF2 boards)""",
)
@click.option(
    "--bootloader/--no-bootloader",
    default=True,
    is_flag=True,
    show_default=True,
    help="""Enter micropython bootloader mode before flashing.""",
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
    bootloader: bool = True,
):
    todo: WorkList = []

    # Ask for missing input if needed	
    

    target_version = clean_version(target_version)
    preview = target_version == "preview"
    # Update all micropython boards to the latest version
    if target_version and port and board and serial_port:
        todo = manual_worklist(target_version, fw_folder, serial_port, board, port, preview)
    elif serial_port:
        if serial_port == "auto":
            todo = auto_worklist(target_version, fw_folder, preview)
        else:
            # just this serial port
            todo = oneport_worklist(target_version, fw_folder, serial_port, preview)

    if flashed := flash_list(todo, fw_folder, erase, bootloader):
        log.info(f"Flashed {len(flashed)} boards")
        show_mcus(flashed, title="Connected boards after flashing")


def oneport_worklist(target_version: str, fw_folder: Path, serial_port: str, preview: bool) -> WorkList:
    """Create a worklist for a single serial-port."""
    conn_boards = [MPRemoteBoard(serial_port)]
    todo = auto_update(conn_boards, target_version, fw_folder, preview=preview)
    show_mcus(conn_boards)
    return todo


def auto_worklist(target_version: str, fw_folder: Path, preview: bool) -> WorkList:
    conn_boards = [MPRemoteBoard(sp) for sp in MPRemoteBoard.connected_boards() if sp not in config.ignore_ports]
    return auto_update(conn_boards, target_version, fw_folder, preview=preview)


def manual_worklist(
    target_version: str, fw_folder: Path, serial_port: str, board: str, port: str, preview: bool
) -> WorkList:
    mcu = MPRemoteBoard(serial_port)
    # TODO : Find a way to avoid needing to specify the port
    # Lookup the matching port and cpu in board_info based in the board name

    mcu.port = port
    mcu.cpu = port if port.startswith("esp") else ""
    mcu.board = board
    firmwares = find_firmware(
        fw_folder=fw_folder,
        board=board,
        version=target_version,
        preview=target_version.lower() == "preview",
        port=port,
    )
    if not firmwares:
        log.error(f"No firmware found for {port} {board} version {target_version}")
        return []
        # use the most recent matching firmware
    return [(mcu, firmwares[-1])]


def flash_list(todo: WorkList, fw_folder: Path, erase: bool, bootloader: bool):
    """Flash a list of boards with the specified firmware."""
    flashed = []
    for mcu, fw_info in todo:
        fw_file = fw_folder / fw_info["filename"]  # type: ignore
        if not fw_file.exists():
            log.error(f"File {fw_file} does not exist, skipping {mcu.board} on {mcu.serialport}")
            continue
        log.info(f"Updating {mcu.board} on {mcu.serialport} to {fw_info['version']}")
        updated = None
        # try:
        if mcu.port in ["samd", "rp2", "nrf"] : #  [k for k, v in PORT_FWTYPES.items() if v == ".uf2"]:
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
