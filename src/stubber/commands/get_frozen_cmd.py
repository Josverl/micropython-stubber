"""Get the frozen stubs for MicroPython."""
##########################################################################################
# get-frozen
##########################################################################################
from pathlib import Path
from typing import List

import click
from loguru import logger as log

import stubber.basicgit as git
import stubber.utils as utils
from stubber.codemod.enrich import enrich_folder
from stubber.freeze.get_frozen import freeze_any
from stubber.utils.config import CONFIG
from stubber.utils.repos import fetch_repos

from .cli import stubber_cli

##########################################################################################


@stubber_cli.command(name="get-frozen")
@click.option(
    "--stub-folder",
    "-stubs",
    default=CONFIG.stub_path.as_posix(),
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    show_default=True,
)
@click.option(
    "--version",
    "--Version",
    "-V",
    "version",
    default="",
    # default=[CONFIG.stable_version],
    show_default=True,
)
@click.option(
    "--pyi/--no-pyi",
    default=True,
    help="Create .pyi files for the (new) frozen modules",
    show_default=True,
)
@click.option(
    "--black/--no-black",
    default=True,
    help="Run black on the (new) frozen modules",
    show_default=True,
)
def cli_get_frozen(
    stub_folder: str = CONFIG.stub_path.as_posix(),
    # path: str = config.repo_path.as_posix(),
    version: str = "",
    pyi: bool = True,
    black: bool = True,
):
    """
    Get the frozen stubs for MicroPython.

    Get the frozen modules for the checked out version of MicroPython
    """

    stub_paths: List[Path] = []

    if version:
        version = utils.clean_version(version, drop_v=False)
        result = fetch_repos(version, CONFIG.mpy_path, CONFIG.mpy_lib_path)
        if not result:
            return -1
    else:
        version = utils.clean_version(git.get_local_tag(CONFIG.mpy_path.as_posix()) or "0.0")
    if not version:
        log.warning(
            "Unable to find the micropython repo in folder : {}".format(CONFIG.mpy_path.as_posix())
        )

    log.info("MicroPython version : {}".format(version))
    # folder/{family}-{version}-frozen
    family = "micropython"
    stub_path = Path(stub_folder) / f"{family}-{utils.clean_version(version, flat=True)}-frozen"
    stub_paths.append(stub_path)
    freeze_any(
        stub_path, version=version, mpy_path=CONFIG.mpy_path, mpy_lib_path=CONFIG.mpy_lib_path
    )
    # Also enrich the frozen modules from the doc stubs if available

    # first create .pyi files so they can be enriched
    utils.do_post_processing(stub_paths, pyi, False)
    family = "micropython"
    docstubs_path = (
        Path(CONFIG.stub_path)
        / f"{family}-{utils.clean_version(version, drop_v=False, flat=True)}-docstubs"
    )
    if docstubs_path.exists():
        log.info(f"Enriching {str(stub_path)} with {docstubs_path}")
        merged = enrich_folder(
            stub_path, docstubs_path, show_diff=False, write_back=True, require_docstub=False
        )
        if merged:
            log.info(f"Enriched {merged} frozen modules from docstubs")
    else:
        log.info(f"No docstubs found at {docstubs_path}")

    log.info("::group:: start post processing of retrieved stubs")
    utils.do_post_processing(stub_paths, False, black)
    log.info("::group:: Done")
