"""Create all variant of createstubs*.py."""
from pathlib import Path
from typing import Union

import click
from loguru import logger as log
from stubber.utils.config import CONFIG
from stubber.variants import create_variants
import stubber

from .cli import stubber_cli


@click.option(
    "--version",
    "--Version",
    "-V",
    "version",
    default=CONFIG.stable_version,
    show_default=True,
    help="The version of mpy-cross to use",
)
@stubber_cli.command(name="make-variants")
@click.pass_context
def cli_variants(
    ctx: click.Context,
    version: str = CONFIG.stable_version,
) -> int:
    """Update all variants of createstubs*.py."""
    board_path = Path(stubber.__file__).parent / "board"
    create_variants(board_path, version=version)

    log.info("Done!")
    return 0
