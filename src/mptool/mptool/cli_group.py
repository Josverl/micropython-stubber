"""
Main entry point for the CLI group.
Additional comands are added in the submodules.
"""

import rich_click as click

from .logger import set_loglevel


def cb_verbose(ctx, param, value):
    """Callback to set the log level to DEBUG if verbose is set"""
    if value:
        set_loglevel("DEBUG")
    else:
        set_loglevel("INFO")
    return value


@click.group()
@click.option("-V", "--verbose", is_flag=True, help="Enables verbose mode", is_eager=True, callback=cb_verbose)
def cli(verbose: bool):
    """Main entry point for the CLI.

    This module provides a CLI to download and flash MicroPython firmware to various boards.
    """
    pass
