"""
Main entry point for the CLI group.
Additional comands are added in the submodules.
"""

import sys

import rich_click as click

from .config import config
from .logger import make_quiet, set_loglevel


def cb_verbose(ctx, param, value):
    """Callback to set the log level to DEBUG if verbose is set"""
    if value and not config.quiet:
        config.verbose = True
        if value > 1:
            set_loglevel("TRACE")
        else:
            set_loglevel("DEBUG")
    else:
        set_loglevel("INFO")
        config.verbose = False
    return value


def cb_interactive(ctx, param, value):
    if value:
        config.interactive = value
    return value


def cb_test(ctx, param, value):
    if value:
        config.tests = value
    return value


def cb_quiet(ctx, param, value):
    if value:
        make_quiet()
    return value


@click.group()
@click.version_option(package_name="mpflash")
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
    "--interactive/--no-interactive",
    "-i/-x",
    is_eager=True,
    help="Suppresses all request for Input.",
    callback=cb_interactive,
    # envvar="MPFLASH_QUIET",
    default=True,
    show_default=True,
)
@click.option(
    "-V",
    "--verbose",
    is_eager=True,
    count=True,
    help="Enables verbose mode.",
    callback=cb_verbose,
)
@click.option(
    "--test",
    is_eager=True,
    help="test a specific feature",
    callback=cb_test,
    multiple=True,
    default=[],
    envvar="MPFLASH_TEST",
    show_default=True,
    metavar="TEST",
)
def cli(**kwargs):
    """mpflash - MicroPython Tool.

    A CLI to download and flash MicroPython firmware to different ports and boards.
    """
    # all functionality is added in the submodules
    pass
