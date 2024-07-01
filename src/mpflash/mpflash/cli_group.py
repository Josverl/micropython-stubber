"""
Main entry point for the CLI group.
Additional comands are added in the submodules.
"""

import rich_click as click

from mpflash.vendor.click_aliases import ClickAliasedGroup

from .config import __version__, config
from .logger import log, make_quiet, set_loglevel


def cb_verbose(ctx, param, value):
    """Callback to set the log level to DEBUG if verbose is set"""
    if value and not config.quiet:
        # log.debug(f"Setting verbose mode to {value}")
        config.verbose = True
        if value > 1:
            set_loglevel("TRACE")
        else:
            set_loglevel("DEBUG")
        log.debug(f"version: {__version__}")
    else:
        set_loglevel("INFO")
        config.verbose = False
    return value


def cb_interactive(ctx, param, value: bool):
    log.trace(f"Setting interactive mode to {value}")
    config.interactive = value
    return value


def cb_test(ctx, param, value):
    if value:
        log.trace(f"Setting tests to {value}")
        config.tests = value
    return value

def cb_usb(ctx, param, value: bool):
    config.usb = bool(value)
    return value


def cb_quiet(ctx, param, value):
    log.trace(f"Setting quiet mode to {value}")
    if value:
        make_quiet()
    return value


@click.group(cls=ClickAliasedGroup)
# @click.group()
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
    "--usb",
    "-u",
    is_eager=True,
    is_flag=True,
    default=False,
    help="Shows USB location of the connected boards.",
    callback=cb_usb,
    show_default=True,
)
@click.option(
    "--test",
    is_eager=True,
    help="Test a specific feature.",
    callback=cb_test,
    multiple=True,
    default=[],
    envvar="MPFLASH_TEST",
    metavar="FLAG",
)
def cli(**kwargs):
    """mpflash - MicroPython flashing tool.

    A CLI to download and flash MicroPython firmware to different ports and boards.
    """
    # all functionality is added in the submodules
    pass
