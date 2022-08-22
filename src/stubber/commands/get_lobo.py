"""
get-lobo (frozen)
"""

import logging
from pathlib import Path
from typing import List

import click
import stubber.get_lobo as get_lobo
import stubber.utils as utils
from stubber.utils.config import CONFIG
# from stubber.utils.my_version import __version__

from .stubber_cli import stubber_cli

##########################################################################################
log = logging.getLogger("stubber")
#########################################################################################



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

    Get the frozen modules for the Loboris v3.2.24 fork of MicroPython
    """

    stub_paths: List[Path] = []

    family = "loboris"
    version = "v3.2.24"
    stub_path = Path(stub_folder) / f"{family}-{utils.clean_version(version, flat=True)}-frozen"
    stub_paths.append(stub_path)
    get_lobo.get_frozen(str(stub_path))
    stub_paths = [stub_path]

    utils.do_post_processing(stub_paths, pyi, black)
