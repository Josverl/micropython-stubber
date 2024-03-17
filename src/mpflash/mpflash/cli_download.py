"""CLI to Download MicroPython firmware for specific ports, boards and versions."""

import pdb
from pathlib import Path
from typing import List, Tuple

import rich_click as click

from mpflash.common import clean_version

from .cli_group import cli
from .cli_list import list_mcus
from .config import config
from .download import download
from .download_input import DownloadParams, ask_missing_params


def connected_ports_boards() -> Tuple[List[str], List[str]]:
    mpr_boards = list_mcus()
    ports = list({b.port for b in mpr_boards})
    boards = list({b.board for b in mpr_boards})
    return ports, boards


@cli.command(
    "download",
    help="Download MicroPython firmware for specific ports, boards and versions.",
)
@click.option(
    "--destination",
    "-d",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=config.firmware_folder,
    show_default=True,
    help="The folder to download the firmware to.",
)
@click.option(
    "--version",
    "-v",
    "versions",
    multiple=True,
    help="The version of MicroPython to to download. Use 'preview' to include preview versions.",
    show_default=True,
    default=["stable"],
)
@click.option(
    "--board",
    "-b",
    "boards",
    multiple=True,
    show_default=True,
    help="The board(s) to download the firmware for.",  # Use '--board all' to download all boards.",
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
    help="""Force download of firmware even if it already exists.""",
    show_default=True,
)
def cli_download(
    **kwargs,
):
    params = DownloadParams(**kwargs)

    if not params.boards:
        # nothing specified - detect connected boards
        params.ports, params.boards = connected_ports_boards()
    # ask for any remaining parameters
    params = ask_missing_params(params)

    params.versions = [clean_version(v, drop_v=True) for v in params.versions]  # remove leading v from version
    # preview is not a version, it is an option to include preview versions
    params.preview = any("preview" in v for v in params.versions)
    params.versions = [v for v in params.versions if "preview" not in v]
    download(
        params.destination,
        params.ports,
        params.boards,
        params.versions,
        params.force,
        params.clean,
        params.preview,
    )
