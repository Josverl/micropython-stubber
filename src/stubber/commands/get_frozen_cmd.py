"""Get the frozen stubs for MicroPython."""

##########################################################################################
# get-frozen
##########################################################################################
from pathlib import Path
from typing import List, Optional

import rich_click as click
from mpflash.logger import log

import stubber.utils as utils
from stubber.codemod.enrich import enrich_folder
from stubber.freeze.get_frozen import freeze_any
from stubber.utils.config import CONFIG
from stubber.utils.repos import fetch_repos

from .cli import stubber_cli

##########################################################################################


@stubber_cli.command(
    name="get-frozen",
    aliases=["get-frozen-stubs", "frozen"],
)
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
    "-v",
    "version",
    default="",
    # default=[CONFIG.stable_version],
    show_default=True,
    help="The version of MicroPython to get the frozen modules for. Use 'preview' to get the latest version from the micropython repo",
)
@click.option(
    "--stubgen/--no-stubgen",
    default=True,
    help="Run stubgen to create .pyi files for the (new) frozen modules",
    show_default=True,
)
@click.option(
    "--black/--no-black",
    default=True,
    help="Run black on the (new) frozen modules",
    show_default=True,
)
def cli_get_frozen(
    stub_folder: Optional[str] = None,
    # path: str = config.repo_path.as_posix(),
    version: str = "",
    stubgen: bool = True,
    black: bool = True,
    autoflake: bool = True,
):
    """
    Get the frozen stubs for MicroPython.

    Get the frozen modules for the checked out version of MicroPython
    """
    # default parameter values
    stub_folder = stub_folder or CONFIG.stub_path.as_posix()
    # FIXME: Stub_folder is not used

    stub_paths: List[Path] = []

    if version:
        version = utils.clean_version(version, drop_v=False)
        result = fetch_repos(version, CONFIG.mpy_path, CONFIG.mpy_lib_path)
        if not result:
            log.error(
                "Failed to fetch repos for version: {} for micropython folder: {} and micropython-lib folder: {}".format(
                    version, CONFIG.mpy_path.as_posix(), CONFIG.mpy_lib_path.as_posix()
                )
            )
            return -1
    # folder/{family}-{version[_preview]}-frozen
    family = "micropython"
    # get the current checked out version
    version = utils.checkedout_version(CONFIG.mpy_path)
    log.info("MicroPython version : {}".format(version))

    stub_path = freeze_any(
        version=version, mpy_path=CONFIG.mpy_path, mpy_lib_path=CONFIG.mpy_lib_path
    )
    stub_paths.append(stub_path)
    # Also enrich the frozen modules from the doc stubs if available

    # first create .pyi files so they can be enriched
    utils.do_post_processing(stub_paths, stubgen=stubgen, black=False, autoflake=False)
    family = "micropython"
    _version = utils.clean_version(version, drop_v=False, flat=True)
    docstubs_path = Path(CONFIG.stub_path) / f"{family}-{_version}-docstubs"
    if docstubs_path.exists():
        log.info(f"Enriching {str(stub_path)} with {docstubs_path}")
        if merged := enrich_folder(
            stub_path,
            docstubs_path,
            show_diff=False,
            write_back=True,
            require_docstub=False,
        ):
            log.info(f"Enriched {merged} frozen modules from docstubs")
    else:
        log.info(f"No docstubs found at {docstubs_path}")

    log.info("::group:: start post processing of retrieved stubs")
    utils.do_post_processing(stub_paths, stubgen=False, black=black, autoflake=autoflake)
    log.info("::group:: Done")
