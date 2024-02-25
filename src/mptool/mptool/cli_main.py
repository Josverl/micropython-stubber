"""Main CLI module for mp_tool."""

import rich_click as click

from .cli_group import cli
from .downloader import download
from .flasher import flash_board, list_boards

# from loguru import logger as log


def mptool():
    """This module provides a CLI to download and flash MicroPython firmware to various boards."""
    cli()


if __name__ == "__main__":
    # cli.add_command(flash_board)
    # cli.add_command(list_boards)
    # cli.add_command(download)
    mptool()
