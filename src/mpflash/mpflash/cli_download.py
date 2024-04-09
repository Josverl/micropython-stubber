"""CLI to Download MicroPython firmware for specific ports, boards and versions."""

from pathlib import Path
from typing import List, Tuple

import rich_click as click

from mpflash.vendored.versions import clean_version

from .ask_input import DownloadParams, ask_missing_params
from .cli_group import cli
from .cli_list import list_mcus
from .config import config
from .download import download


@cli.command(
    "download",
    help="Download MicroPython firmware for specific ports, boards and versions.",
)
@click.option(
    "--destination",
    "-d",
    "fw_folder",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=config.firmware_folder,
    show_default=True,
    help="The folder to download the firmware to.",
)
@click.option(
    "--version",
    "-v",
    "versions",
    default=["stable"],
    multiple=True,
    show_default=True,
    help="The version of MicroPython to to download.",
    metavar="SEMVER, 'stable', 'preview' or '?'",
)
@click.option(
    "--board",
    "-b",
    "boards",
    multiple=True,
    default=[],
    show_default=True,
    help="The board(s) to download the firmware for.",
    metavar="BOARD_ID or ?",
)
@click.option(
    "--clean/--no-clean",
    default=True,
    show_default=True,
    help="""Remove dates and hashes from the downloaded firmware filenames.""",
)
@click.option(
    "--force",
    default=False,
    is_flag=True,
    show_default=True,
    help="""Force download of firmware even if it already exists.""",
)
def cli_download(
    **kwargs,
):
    params = DownloadParams(**kwargs)
    params.versions = list(params.versions)  # remove leading v from version
    params.boards = list(params.boards)
    if not params.boards:
        # nothing specified - detect connected boards
        params.ports, params.boards = connected_ports_boards()
    # ask for any remaining parameters
    params = ask_missing_params(params, action="download")
    params.versions = [clean_version(v, drop_v=True) for v in params.versions]  # remove leading v from version
    assert isinstance(params, DownloadParams)

    download(
        params.fw_folder,
        params.ports,
        params.boards,
        params.versions,
        params.force,
        params.clean,
    )


def connected_ports_boards() -> Tuple[List[str], List[str]]:
    """
    Returns a tuple containing lists of unique ports and boards from the connected MCUs.

    Returns:
        A tuple containing two lists:
            - A list of unique ports where MCUs are connected.
            - A list of unique board names of the connected MCUs.
    """
    mpr_boards = list_mcus()
    ports = list({b.port for b in mpr_boards})
    boards = list({b.board for b in mpr_boards})
    return ports, boards
