
from pathlib import Path
from typing import  Optional


import rich_click as click
from loguru import logger as log

from .cli_group import cli

from .flash_esp import flash_esp
from .flash_stm32 import flash_stm32
from .flash_uf2 import flash_uf2
from .cli_list import show_mcus
from .config import config
from .flash import WorkList, auto_update, enter_bootloader, find_firmware
from .common import clean_version
from mpflash.mpremoteboard import MPRemoteBoard
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
    # stm32_dfu: bool = True,
    bootloader: bool = True,
):
    todo: WorkList = []
    # firmware type selector
    selector = {
        "stm32": ".dfu",  # if stm32_dfu else ".hex",
    }
    target_version = clean_version(target_version)
    preview = target_version == "preview"
    # Update all micropython boards to the latest version
    if target_version and port and board and serial_port:
        # TODO : Find a way to avoid needing to specify the port
        mcu = MPRemoteBoard(serial_port)
        mcu.port = port
        mcu.cpu = port if port.startswith("esp") else ""
        mcu.board = board
        firmwares = find_firmware(
            fw_folder=fw_folder,
            board=board,
            version=target_version,
            preview=target_version.lower() == "preview",
            port=port,
            selector=selector,
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
        todo = auto_update(conn_boards, target_version, fw_folder, preview=preview, selector=selector)

    flashed = []
    for mcu, fw_info in todo:
        fw_file = fw_folder / fw_info["filename"]  # type: ignore
        if not fw_file.exists():
            log.error(f"File {fw_file} does not exist, skipping {mcu.board} on {mcu.serialport}")
            continue
        log.info(f"Updating {mcu.board} on {mcu.serialport} to {fw_info['version']}")

        updated = None
        # try:
        if mcu.port in ["samd", "rp2", "nrf"]:
            if bootloader:
                enter_bootloader(mcu)
            updated = flash_uf2(mcu, fw_file=fw_file, erase=erase)
        elif mcu.port in ["esp32", "esp8266"]:
            #  bootloader is handles by esptool for esp32/esp8266
            updated = flash_esp(mcu, fw_file=fw_file, erase=erase)
        elif mcu.port in ["stm32"]:
            if bootloader:
                enter_bootloader(mcu)
            updated = flash_stm32(mcu, fw_file, erase=erase)
        else:
            log.error(f"Don't (yet) know how to flash {mcu.port}-{mcu.board} on {mcu.serialport}")

        if updated:
            flashed.append(updated)
        else:
            log.error(f"Failed to flash {mcu.board} on {mcu.serialport}")

    if flashed:
        log.info(f"Flashed {len(flashed)} boards")
        show_mcus(flashed, title="Connected boards after flashing")
