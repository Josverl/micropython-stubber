"""mpflash is a CLI to download and flash MicroPython firmware to various boards."""

# import rich_click as click

import os

import click
from loguru import logger as log

from .cli_download import cli_download
from .cli_flash import cli_flash_board
from .cli_group import cli
from .cli_list import cli_list_mcus
from .errors import EXIT_ERROR, EXIT_CANCELLED


def mpflash():
    cli.add_command(cli_list_mcus)
    cli.add_command(cli_download)
    cli.add_command(cli_flash_board)

    # cli(auto_envvar_prefix="MPFLASH")
    if False and os.environ.get("COMPUTERNAME").lower().startswith("josverl"):
        # intentional less error suppression on dev machine
        result = cli(standalone_mode=False)
    else:
        try:
            result = cli(standalone_mode=False)
        except AttributeError as e:
            log.error(f"Error: {e}")
            exit(EXIT_ERROR)
        except (click.exceptions.ClickException, click.exceptions.UsageError) as e:
            log.error(f"Error: {e}")
            exit(EXIT_ERROR)
        except click.exceptions.Abort as e:
            # Aborted - Ctrl-C
            log.info(f"Cancelled by user")
            exit(EXIT_CANCELLED)
        # return result
        exit(result)


if __name__ == "__main__":
    mpflash()
