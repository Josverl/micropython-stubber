"""mpflash is a CLI to download and flash MicroPython firmware to various boards."""

import rich_click as click

from .cli_group import cli
from .downloader import cli_download
from .flasher import cli_flash_board
from .list import cli_list_mcus

# from loguru import logger as log


def mpflash():
    # cli.add_command(flash_board)
    # cli.add_command(list_boards)
    # cli.add_command(download)
    cli(auto_envvar_prefix="MPFLASH")


if __name__ == "__main__":
    mpflash()
