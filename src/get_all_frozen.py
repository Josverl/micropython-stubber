#!/usr/bin/env python3
"""
Collect modules and python stubs from other projects and stores them in the all_stubs folder
The all_stubs folder should be mapped/symlinked to the micropython_stubs/stubs repo/folder

 1) get cpython core modules
 2) get micropython frozen modules for the CURRENT checked out version
 3) get Loboris frozen modules (no longer maintained)
 4) Generate/update type hint files (pyi) for all stubs.

"""
# pylint: disable= line-too-long, W1202
# Copyright (c) 2020 Jos Verlinde
# MIT license

from typing import List
import logging
import basicgit as git
import utils
from pathlib import Path
import click

import get_cpython
import get_mpy
import get_lobo

# todo: add frozen modules for : pycopy
# import freezer_pycopy

log = logging.getLogger(__name__)


##########################################################################################
# command line interface
##########################################################################################

STUB_FOLDER = "./all-stubs"
MPY_FOLDER = "./micropython"
MPY_LIB_FOLDER = "./micropython-lib"


@click.command()
@click.option("--stub-folder", "-stubs", default=STUB_FOLDER, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--micropython", "mpy_folder", default=MPY_FOLDER, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--micropython-lib", "mpy_lib_folder", default=MPY_LIB_FOLDER, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--version", default="", type=str, help="Version number to use. Default: Current Git tag")
@click.option("--mpy", default=False, is_flag=True, help="Download the micropython frozen modules.")
@click.option("--lobo", default=False, is_flag=True, help="Download the loboris frozen modules.")
@click.option("--core", default=False, is_flag=True, help="Download the cpython core modules.")
@click.option(
    "--core-type",
    type=click.Choice(["pycopy", "micropython"], case_sensitive=False),
    default="pycopy",
    help="Download CPthon modules Pycopy or Micropython version. Default: Pycopy",
)
@click.option("--pyi/--no-pyi", default=True, help="Create .pyi files for the (new) frozen modules")
@click.option("--all", default=False, is_flag=True, help="Get all frozen modules")
def get_all(
    stub_folder: str = STUB_FOLDER,
    mpy_folder: str = MPY_FOLDER,
    mpy_lib_folder: str = MPY_LIB_FOLDER,
    version: str = "",
    core: bool = False,
    core_type: str = "pycopy",  # pycopy or Micropython CPython stubs
    mpy: bool = False,
    lobo: bool = False,
    pyi: bool = True,
    all: bool = False,
):
    "get all frozen modules for the current version of micropython"
    if not (core or mpy or lobo or all):
        log.warning("Nothing to do")
        exit(2)

    stub_paths: List[Path] = []
    if core or all:
        req_filename = f"requirements-core-{core_type}.txt"
        log.info(f"::group:: Get Cpython core :{core_type}")
        stub_path = Path(stub_folder) / "cpython_core"
        get_cpython.get_core(stub_path=str(stub_path), requirements=req_filename)
        stub_paths.append(stub_path)

    if len(version) == 0:
        version = utils.clean_version(git.get_tag(mpy_folder) or "0.0")
    if mpy or all:
        if version:
            log.info("MicroPython version : {}".format(version))
            # folder/{family}-{version}-frozen
            family = "micropython"
            stub_path = Path(stub_folder) / f"{family}-{utils.flat_version(version)}-frozen"
            stub_paths.append(stub_path)
            get_mpy.get_frozen(str(stub_path), version=version, mpy_path=mpy_folder, lib_path=mpy_lib_folder)

        else:
            log.warning("Unable to find the micropython repo in folder : {}".format(mpy_folder))
    if lobo or all:
        family = "loboris"
        version = "v3.2.24"
        stub_path = Path(stub_folder) / f"{family}-{utils.flat_version(version)}-frozen"
        stub_paths.append(stub_path)
        get_lobo.get_frozen(str(stub_path))

    if pyi:
        for pth in stub_paths:
            log.info("Generate type hint files (pyi) in folder: {}".format(pth))
            utils.generate_pyi_files(pth)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)-8s:%(message)s", level=logging.INFO)
    get_all()
    # Click: Debugging
    # get_all(["-stubs", ".\\scratch\\stubs\\", "--core", "--no-mpy", "--core-type", "micropython", "--no-pyi"])
