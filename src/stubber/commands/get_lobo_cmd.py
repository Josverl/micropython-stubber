"""
get-lobo (frozen)
"""

from pathlib import Path
from typing import List

import click
import stubber.get_lobo as get_lobo
import stubber.utils as utils
from loguru import logger as log
from stubber.commands.cli import stubber_cli
from stubber.utils.config import CONFIG


@stubber_cli.command(name="get-lobo")
@click.option(
    "--stub-folder",
    "-stubs",
    default=CONFIG.stub_path.as_posix(),
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    show_default=True,
)
@click.option("--pyi/--no-pyi", default=True, help="Create .pyi files for the (new) frozen modules", show_default=True)
@click.option("--black/--no-black", default=True, help="Run black on the (new) frozen modules", show_default=True)
def cli_get_lobo(
    stub_folder: str = CONFIG.stub_path.as_posix(),
    pyi: bool = True,
    black: bool = True,
):
    """
    Get the frozen stubs for Lobo-esp32.

    """
    log.info("Get the frozen modules Loboris v3.2.24")

    stub_paths: List[Path] = []

    family = "loboris"
    version = "v3.2.24"
    stub_path = Path(stub_folder) / f"{family}-{utils.clean_version(version, flat=True)}-frozen"
    stub_paths.append(stub_path)
    get_lobo.get_frozen(stub_path)
    stub_paths = [stub_path]

    log.info(f"::group:: start post processing of retrieved stubs")
    utils.do_post_processing(stub_paths, pyi, black)
    log.info(f"::group:: Done")
