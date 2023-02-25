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
    help="multiple: ",
)
@stubber_cli.command(name="variants")
@click.pass_context
def cli_variants(
    ctx: click.Context,
    version: str = CONFIG.stable_version,
) -> int:
    """Create all variant of createstubs*.py."""
    board_path = Path(stubber.__file__).parent / "board"
    create_variants(board_path, version=version)

    log.info("Done!")
    return 0
