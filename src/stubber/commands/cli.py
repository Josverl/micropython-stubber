"""
command line interface - main group
"""
import sys

import click
from loguru import logger as log
from stubber.utils.my_version import __version__


@click.group(chain=True)
@click.version_option(package_name="micropython-stubber", prog_name="micropython-stubber✏️ ")
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    help="-v for DEBUG, -v -v for TRACE",
    is_eager=True,
)
@click.pass_context
def stubber_cli(ctx: click.Context, verbose: int = 0) -> None:
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    ctx.ensure_object(dict)
    # replace std log handler with a custom one capped on INFO level
    log.remove()
    level = {0: "INFO", 1: "DEBUG", 2: "TRACE"}.get(verbose, "TRACE")
    if level == "INFO":
        format_str = (
            "<green>{time:YY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module: <18}</cyan> - <level>{message}</level>"
        )
    else:
        format_str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    log.add(sys.stderr, level=level, backtrace=True, diagnose=True, colorize=True, format=format_str)
    log.info(f"micropython-stubber {__version__}")

    if level != "INFO":
        log.info(f"Log level set to {level}")
    # save info in context for other CLICK modules to use
    ctx.obj["loglevel"] = level
    ctx.obj["verbose"] = verbose
