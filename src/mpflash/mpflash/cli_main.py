"""mpflash is a CLI to download and flash MicroPython firmware to various boards."""

# import rich_click as click

from .cli_download import cli_download
from .cli_flash import cli_flash_board
from .cli_group import cli
from .cli_list import cli_list_mcus

# from loguru import logger as log


def mpflash():
    cli.add_command(cli_flash_board)
    cli.add_command(cli_list_mcus)
    cli.add_command(cli_download)
    # cli(auto_envvar_prefix="MPFLASH")
    try:
        cli()
    except AttributeError as e:
        print(f"Error: {e}")
        exit(-1)


if __name__ == "__main__":
    mpflash()
