"""
command line interface - main group
"""

import sys

from mpflash.vendor.click_aliases import ClickAliasedGroup
import rich_click as click
from mpflash.logger import log, set_loglevel as mpf_set_loglevel
from stubber import __version__


@click.group(chain=True, cls=ClickAliasedGroup)
@click.version_option(package_name="micropython-stubber", prog_name="micropython-stubber✏️ ")
@click.option(
    "-V",
    "-V",
    "--verbose",
    count=True,
    default=0,
    help="-V for DEBUG, -VV for TRACE",
    is_eager=True,
)
@click.pass_context
def stubber_cli(ctx: click.Context, verbose: int = 0) -> None:
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    ctx.ensure_object(dict)
    # replace std log handler with a custom one capped on INFO level
    level = set_loglevel(verbose)

    if level != "INFO":
        log.info(f"Log level set to {level}")
    # save info in context for other CLICK modules to use
    ctx.obj["loglevel"] = level
    ctx.obj["verbose"] = verbose


def set_loglevel(verbose: int) -> str:
    """Set log level based on verbose level
    Get the level from the verbose setting (0=INFO, 1=DEBUG, 2=TRACE)
    Set the format string, based on the level.
    Add the handler to the logger, with the level and format string.
    Return the level
    """
    level = {0: "INFO", 1: "DEBUG", 2: "TRACE"}.get(verbose, "TRACE")
    # reuse mpflash logger
    mpf_set_loglevel(level)
    log.info(f"micropython-stubber {__version__}")
    return level
