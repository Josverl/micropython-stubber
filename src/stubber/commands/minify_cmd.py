"""Minify createstubs*.py."""
##########################################################################################
# minify
##########################################################################################
from pathlib import Path
from typing import Union

import click
from loguru import logger as log
from stubber.minify import minify, cross_compile
import stubber

from .cli import stubber_cli


@stubber_cli.command(name="minify")
@click.option("--source", "-s", default="createstubs.py", type=click.Path(file_okay=True, dir_okay=False), show_default=True)
@click.option("--diff", "-d", help="Show the functional changes made to the source script.", default=False, is_flag=True)
@click.option("--compile", "-c", "-xc", "compile", help="Cross compile after minification.", default=False, is_flag=True)
@click.option("--all", "-a", help="Minify all variants (normal, _mem and _db).", default=False, is_flag=True)
@click.option(
    "--report/--no-report",
    "keep_report",
    help="Keep or disable minimal progress reporting in the minified version.",
    default=True,
    show_default=True,
)
@click.pass_context
def cli_minify(
    ctx: click.Context,
    source: Union[str, Path],
    keep_report: bool,
    diff: bool,
    compile: bool,
    all: bool,
) -> int:
    """
    Minify createstubs*.py.

    Creates a minified version of the SOURCE micropython file in TARGET (file or folder).
    The goal is to use less memory / not to run out of memory, while generating MCU stubs.
    """
    if all:
        sources = ["createstubs.py", "createstubs_mem.py", "createstubs_db.py"]
    else:
        sources = [source]
    log.trace(f"sources: {sources}")
    for source in sources:
        # TODO: Check if module resources should not be retrieved via API (e.g. via importlib.resources)
        src = Path(stubber.__file__).parent / "board" / source
        dst = src.with_name(src.stem + "_min.py")
        min_dest = src.with_name(src.stem + "_mpy.mpy")
        log.info(f"\nMinifying {src}...")
        minify(src, dst, keep_report, diff)
        if compile:
            log.info("Cross compiling...")
            cross_compile(dst, min_dest)

    log.info("Done!")
    return 0
