"""Create all variant of createstubs*.py."""

from pathlib import Path

import rich_click as click
from mpflash.logger import log
from packaging.version import InvalidVersion, Version

import stubber
from stubber.commands.cli import stubber_cli
from stubber.utils.config import CONFIG
from stubber.variants import create_variants


def _version_supports_minify(version: str) -> bool:
    """Return True if the mpy-cross version supports minified output (> 1.18)."""
    if not version or version in ("master", "preview", "latest"):
        return True
    try:
        return Version(version.lstrip("v")) > Version("1.18")
    except InvalidVersion:
        return True


@click.option(
    "--target",
    "-t",
    "target_folder",
    default=None,
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    help="Target folder for the createstubs*.py/.mpy files",
    show_default=True,
)
@click.option(
    "--version",
    "-v",
    "version",
    default=CONFIG.stable_version,
    show_default=True,
    help="The version of mpy-cross to use",
)
@click.option(
    "--minify/--no-minify",
    "minify",
    default=True,
    help="Minify createstubs*.py before compiling (automatically disabled for mpy-cross <= v1.18)",
)
@stubber_cli.command(name="variants", aliases=["make-variants"])
@click.pass_context
def cli_variants(
    ctx: click.Context,
    target_folder: str = "",
    version: str = CONFIG.stable_version,
    minify: bool = True,
) -> int:
    """Update all variants of createstubs*.py."""
    board_path = Path(stubber.__file__).parent / "board"
    if target_folder:
        target_path = Path(target_folder).absolute()
        target_path.mkdir(parents=True, exist_ok=True)
    else:
        target_path = board_path

    if minify and not _version_supports_minify(version):
        log.info(f"mpy-cross version {version} <= 1.18: minification disabled to avoid SyntaxError")
        minify = False

    create_variants(board_path, target_path=target_path, version=version, minify=minify)

    log.info("Done!")
    return 0
