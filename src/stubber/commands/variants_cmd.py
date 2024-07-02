"""Create all variant of createstubs*.py."""

from pathlib import Path

import rich_click as click
from mpflash.logger import log
from stubber.utils.config import CONFIG
from stubber.variants import create_variants
import stubber

from .cli import stubber_cli


@click.option(
    "--version",
    "-v",
    "version",
    default=CONFIG.stable_version,
    show_default=True,
    help="The version of mpy-cross to use",
)
@click.option(
    "--target",
    "-t",
    "target_folder",
    default=None,
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    help="Target folder for the createstubs*.py/.mpy files",
    show_default=True,
)
@stubber_cli.command(name="make-variants")
@click.pass_context
def cli_variants(
    ctx: click.Context,
    target_folder: str = "",
    version: str = CONFIG.stable_version,
) -> int:
    """Update all variants of createstubs*.py."""
    board_path = Path(stubber.__file__).parent / "board"
    if target_folder:
        target_path = Path(target_folder).absolute()
        target_path.mkdir(parents=True, exist_ok=True)
    else:
        target_path = board_path
    create_variants(board_path, target_path=target_path, version=version)

    log.info("Done!")
    return 0
