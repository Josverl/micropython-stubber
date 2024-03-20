from pathlib import Path

import rich_click as click
from loguru import logger as log

from mpflash.mpboard_id.api import find_mp_board

from .ask_input import FlashParams, ask_missing_params
from .cli_download import connected_ports_boards
from .cli_group import cli
from .cli_list import show_mcus
from .common import clean_version
from .config import config
from .flash import WorkList, auto_update, enter_bootloader, find_firmware
from .flash_esp import flash_esp
from .flash_stm32 import flash_stm32
from .flash_uf2 import flash_uf2
from .mpremoteboard import MPRemoteBoard

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
    "version",  # single version
    default="stable",
    multiple=False,
    show_default=True,
    help="The version of MicroPython to flash.",
    metavar="SEMVER, 'stable', 'preview' or '?'",
)
@click.option(
    "--serial",
    "--serial-port",
    "-s",
    "serial",
    default="auto",
    show_default=True,
    help="Which serial port(s) to flash",
    metavar="SERIAL_PORT",
)
@click.option(
    "--port",
    "-p",
    "ports",
    help="The MicroPython port to flash",
    metavar="PORT",
    default=[],
    multiple=True,
)
@click.option(
    "--board",
    "-b",
    "boards",
    multiple=False,
    default=[],
    help="The MicroPython board ID to flash. If not specified will try to read the BOARD_ID from the connected MCU.",
    metavar="BOARD_ID or ?",
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
def cli_flash_board(**kwargs):
    todo: WorkList = []

    # version to versions
    if "version" in kwargs:
        kwargs["versions"] = [kwargs.pop("version")]
    params = FlashParams(**kwargs)
    print(f"{params=}")
    # print(f"{params.version=}")
    print(f"{params.versions=}")
    if not params.boards:
        # nothing specified - detect connected boards
        params.ports, params.boards = connected_ports_boards()
    # Ask for missing input if needed
    params = ask_missing_params(params, action="flash")
    # TODO: Just in time Download of firmware

    assert isinstance(params, FlashParams)

    if len(params.versions) > 1:
        print(repr(params.versions))
        log.error(f"Only one version can be flashed at a time, not {params.versions}")
        return
    params.versions = [clean_version(v) for v in params.versions]
    if params.versions[0] and params.boards[0] and params.serial:
        # update a single board
        todo = manual_worklist(
            params.versions[0],
            params.fw_folder,
            params.serial,
            params.boards[0],
            # params.ports[0],
        )
    elif params.serial:
        if params.serial == "auto":
            # Update all micropython boards to the latest version
            todo = auto_worklist(params.versions[0], params.fw_folder)
        else:
            # just this serial port on auto
            todo = oneport_worklist(
                params.versions[0],
                params.fw_folder,
                params.serial,
            )

    if flashed := flash_list(
        todo,
        params.fw_folder,
        params.erase,
        params.bootloader,
    ):
        log.info(f"Flashed {len(flashed)} boards")
        show_mcus(flashed, title="Connected boards after flashing")


def oneport_worklist(
    version: str,
    fw_folder: Path,
    serial_port: str,
    # preview: bool,
) -> WorkList:
    """Create a worklist for a single serial-port."""
    conn_boards = [MPRemoteBoard(serial_port)]
    todo = auto_update(conn_boards, version, fw_folder)
    show_mcus(conn_boards)
    return todo


def auto_worklist(version: str, fw_folder: Path) -> WorkList:
    conn_boards = [MPRemoteBoard(sp) for sp in MPRemoteBoard.connected_boards() if sp not in config.ignore_ports]
    return auto_update(conn_boards, version, fw_folder)


def manual_worklist(
    version: str,
    fw_folder: Path,
    serial_port: str,
    board: str,
    # port: str,
) -> WorkList:
    mcu = MPRemoteBoard(serial_port)
    # TODO : Find a way to avoid needing to specify the port
    # Lookup the matching port and cpu in board_info based in the board name
    port = find_mp_board(board)["port"]
    mcu.port = port
    mcu.cpu = port if port.startswith("esp") else ""
    mcu.board = board
    firmwares = find_firmware(fw_folder=fw_folder, board=board, version=version, port=port)
    if not firmwares:
        log.error(f"No firmware found for {port} {board} version {version}")
        return []
        # use the most recent matching firmware
    return [(mcu, firmwares[-1])]


def flash_list(
    todo: WorkList,
    fw_folder: Path,
    erase: bool,
    bootloader: bool,
):
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
        if mcu.port in ["samd", "rp2", "nrf"]:  #  [k for k, v in PORT_FWTYPES.items() if v == ".uf2"]:
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
