from pathlib import Path

import rich_click as click
from loguru import logger as log

from mpflash.errors import MPFlashError
from mpflash.mpboard_id import find_stored_board
from mpflash.vendor.versions import clean_version

from .ask_input import FlashParams, ask_missing_params
from .cli_download import connected_ports_boards
from .cli_group import cli
from .cli_list import show_mcus
from .config import config
from .flash import flash_list
from .worklist import WorkList, full_auto_worklist, manual_worklist, single_auto_worklist

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
    "--bootloader/--no-bootloader",
    default=True,
    is_flag=True,
    show_default=True,
    help="""Enter micropython bootloader mode before flashing.""",
)
def cli_flash_board(**kwargs):
    # version to versions, board to boards
    kwargs["versions"] = [kwargs.pop("version")] if kwargs["version"] != None else []
    if kwargs["board"] is None:
        kwargs["boards"] = []
        kwargs.pop("board")
    else:
        kwargs["boards"] = [kwargs.pop("board")]

    params = FlashParams(**kwargs)
    if not params.boards or params.boards == []:
        # nothing specified - detect connected boards
        params.ports, params.boards = connected_ports_boards()
    else:
        for board_id in params.boards:
            if board_id == "":
                params.boards.remove(board_id)
                continue
            if " " in board_id:
                try:
                    info = find_stored_board(board_id)
                    if info:
                        log.info(f"Resolved board description: {info['board']}")
                        params.boards.remove(board_id)
                        params.boards.append(info["board"])
                except Exception as e:
                    log.warning(f"unable to resolve board description: {e}")

    # Ask for missing input if needed
    params = ask_missing_params(params, action="flash")
    if not params:  # Cancelled by user
        exit(1)
    # TODO: Just in time Download of firmware

    assert isinstance(params, FlashParams)

    if len(params.versions) > 1:
        log.error(f"Only one version can be flashed at a time, not {params.versions}")
        raise MPFlashError("Only one version can be flashed at a time")
    # if len(params.boards) > 1:
    #     log.error(f"Only one board can be flashed at a time, not {params.boards}")
    #     raise MPFlashError("Only one board can be flashed at a time")

    params.versions = [clean_version(v) for v in params.versions]
    worklist: WorkList = []
    # if serial port == auto and there are one or more specified/detected boards
    if params.serial == "auto" and params.boards:
        worklist = full_auto_worklist(version=params.versions[0], fw_folder=params.fw_folder)
    elif params.versions[0] and params.boards[0] and params.serial:
        # A single serial port including the board / variant
        worklist = manual_worklist(
            params.versions[0],
            params.fw_folder,
            params.serial,
            params.boards[0],
        )
    else:
        # just this serial port on auto
        worklist = single_auto_worklist(
            serial_port=params.serial,
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
