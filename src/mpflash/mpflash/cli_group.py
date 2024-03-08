"""
Main entry point for the CLI group.
Additional comands are added in the submodules.
"""

import rich_click as click

from .config import config
from .logger import make_quiet, set_loglevel


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
    return value


def cb_quiet(ctx, param, value):
    if value:
        make_quiet()
    return value


@click.group()
@click.option(
    "--quiet",
    "-q",
    is_eager=True,
    is_flag=True,
    help="Suppresses all output.",
    callback=cb_quiet,
    envvar="MPFLASH_QUIET",
    show_default=True,
)
@click.option(
    "-V",
    "--verbose",
    is_eager=True,
    is_flag=True,
    help="Enables verbose mode.",
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
def cli(quiet: bool, **kwargs):
    """mpflash - MicroPython Tool.

    A CLI to download and flash MicroPython firmware to different ports and boards.
    """
    # all functionality is added in the submodules
    pass
