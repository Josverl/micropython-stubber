from pathlib import Path
from typing import List

import rich_click as click
from loguru import logger as log

from mpflash.ask_input import ask_missing_params
from mpflash.cli_download import connected_ports_boards
from mpflash.cli_group import cli
from mpflash.cli_list import show_mcus
from mpflash.common import BootloaderMethod, FlashParams, Params
from mpflash.config import config
from mpflash.errors import MPFlashError
from mpflash.flash import flash_list
from mpflash.flash.worklist import WorkList, full_auto_worklist, manual_worklist, single_auto_worklist
from mpflash.mpboard_id import find_known_board
from mpflash.mpremoteboard import MPRemoteBoard
from mpflash.versions import clean_version

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
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
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
    default=["*"],
    multiple=True,
    show_default=True,
    help="Which serial port(s) (or globs) to flash",
    metavar="SERIALPORT",
)
@click.option(
    "--ignore",
    "-i",
    is_eager=True,
    help="Serial port(s) to ignore. Defaults to MPFLASH_IGNORE.",
    multiple=True,
    default=[],
    envvar="MPFLASH_IGNORE",
    show_default=True,
    metavar="SERIALPORT",
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
    "board",  # single board
    multiple=False,
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
    help="""Erase flash before writing new firmware. (Not supported on UF2 boards)""",
)
@click.option(
    "--bootloader",
    "-bl",
    "bootloader",
    type=click.Choice([e.value for e in BootloaderMethod]),
    default="auto",
    show_default=True,
    help="""How to enter the (MicroPython) bootloader before flashing.""",
)
def cli_flash_board(**kwargs) -> int:
    # version to versions, board to boards
    kwargs["versions"] = [kwargs.pop("version")] if kwargs["version"] != None else []
    if kwargs["board"] is None:
        kwargs["boards"] = []
        kwargs.pop("board")
    else:
        kwargs["boards"] = [kwargs.pop("board")]

    params = FlashParams(**kwargs)
    params.versions = list(params.versions)
    params.ports = list(params.ports)
    params.boards = list(params.boards)
    params.serial = list(params.serial)
    params.ignore = list(params.ignore)
    params.bootloader = BootloaderMethod(params.bootloader)

    # make it simple for the user to flash one board by asking for the serial port if not specified
    if params.boards == ["?"] and params.serial == "*":
        params.serial = ["?"]

    # Detect connected boards if not specified,
    # and ask for input if boards cannot be detected
    all_boards: List[MPRemoteBoard] = []
    if not params.boards:
        # nothing specified - detect connected boards
        params.ports, params.boards, all_boards = connected_ports_boards(include=params.ports, ignore=params.ignore)
        if params.boards == []:
            # No MicroPython boards detected, but it could be unflashed or in bootloader mode
            # Ask for serial port and board_id to flash
            params.serial = ["?"]
            params.boards = ["?"]
            # assume manual mode if no board is detected
            params.bootloader = BootloaderMethod("manual")
    else:
        resolve_board_ids(params)

    # Ask for missing input if needed
    params = ask_missing_params(params)
    if not params:  # Cancelled by user
        return 2
    # TODO: Just in time Download of firmware

    assert isinstance(params, FlashParams)

    if len(params.versions) > 1:
        log.error(f"Only one version can be flashed at a time, not {params.versions}")
        raise MPFlashError("Only one version can be flashed at a time")

    params.versions = [clean_version(v) for v in params.versions]
    worklist: WorkList = []
    # if serial port == auto and there are one or more specified/detected boards
    if params.serial == ["*"] and params.boards:
        if not all_boards:
            log.trace("No boards detected yet, scanning for connected boards")
            _, _, all_boards = connected_ports_boards(include=params.ports, ignore=params.ignore)
        worklist = full_auto_worklist(
            all_boards=all_boards,
            version=params.versions[0],
            fw_folder=params.fw_folder,
            include=params.serial,
            ignore=params.ignore,
        )
    elif params.versions[0] and params.boards[0] and params.serial:
        # A one or more  serial port including the board / variant
        worklist = manual_worklist(
            params.serial[0],
            board_id=params.boards[0],
            version=params.versions[0],
            fw_folder=params.fw_folder,
        )
    else:
        # just this serial port on auto
        worklist = single_auto_worklist(
            serial=params.serial[0],
            version=params.versions[0],
            fw_folder=params.fw_folder,
        )

    if flashed := flash_list(
        worklist,
        params.fw_folder,
        params.erase,
        params.bootloader,
    ):
        log.info(f"Flashed {len(flashed)} boards")
        show_mcus(flashed, title="Updated boards after flashing")
        return 0
    else:
        log.error("No boards were flashed")
        return 1


def resolve_board_ids(params: Params):
    """Resolve board descriptions to board_id, and remove empty strings from list of boards"""
    for board_id in params.boards:
        if board_id == "":
            params.boards.remove(board_id)
            continue
        if " " in board_id:
            try:
                if info := find_known_board(board_id):
                    log.info(f"Resolved board description: {info.board_id}")
                    params.boards.remove(board_id)
                    params.boards.append(info.board_id)
            except Exception as e:
                log.warning(f"Unable to resolve board description: {e}")
