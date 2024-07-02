"""Get core CPython stubs from PyPi."""

##########################################################################################
# core
##########################################################################################

from pathlib import Path
from typing import List

import rich_click as click
from mpflash.logger import log

import stubber.get_cpython as get_cpython
import stubber.utils as utils
from stubber.utils.config import CONFIG

from .cli import stubber_cli

##########################################################################################
# log = logging.getLogger("stubber")
#########################################################################################


@stubber_cli.command(name="get-core")
@click.option(
    "--stub-folder",
    "-stubs",
    default=CONFIG.stub_path.as_posix(),
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    show_default=True,
)
@click.option(
    "--stubgen/--no-stubgen",
    default=True,
    help="run stubgen to create .pyi files for the (new) frozen modules",
    show_default=True,
)
@click.option(
    "--black/--no-black",
    default=True,
    help="Run black on the (new) frozen modules",
    show_default=True,
)
def cli_get_core(
    stub_folder: str = "",
    # core_type: str = "pycopy",  # pycopy or Micropython CPython stubs
    stubgen: bool = True,
    black: bool = True,
):
    """
    Download core CPython stubs from PyPi.

    Get the core (CPython compat) modules for both MicroPython and Pycopy.
    """
    # default parameter values
    stub_folder = stub_folder or CONFIG.stub_path.as_posix()

    stub_paths: List[Path] = []
    for core_type in ["pycopy", "micropython"]:
        log.info(f"::group:: Get Cpython core :{core_type}")
        req_filename = f"requirements-core-{core_type}.txt"
        stub_path = Path(stub_folder) / f"cpython_core-{core_type}"

        get_cpython.get_core(
            stub_path=stub_path.as_posix(), requirements=req_filename, family=core_type
        )
        stub_paths.append(stub_path)

    log.info("::group:: start post processing of retrieved stubs")
    utils.do_post_processing(stub_paths, stubgen=stubgen, black=black, autoflake=True)
    log.info("::group:: Done")
