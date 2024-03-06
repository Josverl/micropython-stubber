"""
Main entry point for the CLI group.
Additional comands are added in the submodules.
"""

from typing import List

import rich_click as click

from .config import config
from .logger import set_loglevel


def cb_verbose(ctx, param, value):
    """Callback to set the log level to DEBUG if verbose is set"""
    if value:
        set_loglevel("DEBUG")
    else:
        set_loglevel("INFO")
    return value


def cb_ignore(ctx, param, value):
    if value:
        config.ignore_ports = list(value)
        print(repr(config.ignore_ports))
    return value


@click.group()
@click.option(
    "-V",
    "--verbose",
    is_flag=True,
    help="Enables verbose mode.",
    is_eager=True,
    callback=cb_verbose,
)
@click.option(
    "--ignore",
    "-i",
    is_eager=True,
    help="Serial port(s) to ignore. Defaults to MPFLASH_IGNORE.",
    callback=cb_ignore,
    multiple=True,
    default=[],
    envvar="MPFLASH_IGNORE",
    show_default=True,
    metavar="SERIALPORT",
)
def cli(verbose: bool, ignore: List[str], **kwargs):
    """mpflash - MicroPython Tool.

    A CLI to download and flash MicroPython firmware to different ports and boards.
    """
    pass
