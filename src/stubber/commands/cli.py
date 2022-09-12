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
    help="-v for DEBUG",
    is_eager=True,
)
@click.pass_context
def stubber_cli(ctx, verbose: int = 0):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    ctx.ensure_object(dict)
    # replace std log handler with a custom one capped on INFO level
    log.remove()
    level = {0: "INFO", 1: "DEBUG", 2: "TRACE"}.get(verbose, "INFO")
    if level == "INFO":
        format = "<green>{time:YY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{module: <18}</cyan> - <level>{message}</level>"
    else:
        format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    log.add(sys.stderr, level=level, backtrace=True, diagnose=True, colorize=True, format=format)
    log.info(f"micropython-stubber {__version__}")

    ctx.obj["loglevel"] = level
    ctx.obj["verbose"] = verbose
