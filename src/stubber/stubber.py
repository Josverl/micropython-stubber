#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""create porcess and maintain stubs for micropython"""
from typing import Dict, Union, List
from pathlib import Path
import os
import click
import logging


from .minify import minify

from . import utils
from . import basicgit as git
from . import get_cpython
from . import get_mpy
from . import get_lobo
from .stubs_from_docs import generate_from_rst
from .update_fallback import update_fallback, RELEASED
from .version import __version__


##########################################################################################
log = logging.getLogger(__name__)


config = utils.readconfig()
##########################################################################################


##########################################################################################
# command line interface - main group
##########################################################################################


@click.group(chain=True)
@click.version_option(package_name="micropython-stubber", prog_name="micropython-stubber✏️ ")
@click.option("--verbose", "-vv", is_flag=True, default=False)
@click.option("--debug", "-vvv", is_flag=True, default=False)

# TODO: add stubfolder to top level and pass using context
# @click.option("--stub-folder", "-stubs", default=config["stub-folder"], type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.pass_context
def stubber_cli(ctx, verbose=False, debug=False):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    ctx.ensure_object(dict)

    # Set log level
    lvl = logging.WARNING
    if verbose:
        lvl = logging.INFO
    if debug:
        lvl = logging.DEBUG
    ctx.obj["loglevel"] = lvl

    logging.basicConfig(level=lvl)
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(lvl)


##########################################################################################
# clone
##########################################################################################
@stubber_cli.command(name="clone")
@click.option("--mpy/--no-mpy", "-m/-nm", help="clone micropython", default=True, is_flag=True)
@click.option("--mpy-lib/--no-mpy-lib", "-l/-nl", help="clone micropython-lib", default=True, is_flag=True)
@click.option("--path", "-p", default=config["repo-folder"], type=click.Path(file_okay=False, dir_okay=True))
def cli_clone(mpy: bool, mpy_lib: bool, path: Union[str, Path]):
    """
    Clone the micropython repos locally.

    The local repos are used to generate frozen-stubs and doc-stubs.
    """
    dest_path = Path(path)
    if not dest_path.exists():
        os.mkdir(dest_path)
    if mpy:
        git.clone(remote_repo="https://github.com/micropython/micropython.git", path=dest_path / config["mpy-folder"])
    if mpy_lib:
        git.clone(remote_repo="https://github.com/micropython/micropython-lib.git", path=dest_path / config["mpy-lib-folder"])


##########################################################################################
# stub
##########################################################################################
@stubber_cli.command(name="stub")
@click.option("--source", "-s", type=click.Path(exists=True, file_okay=True, dir_okay=True))
def cli_stub(source: Union[str, Path]):
    "Create or update .pyi type hint files."

    log.info("Generate type hint files (pyi) in folder: {}".format(source))
    OK = utils.generate_pyi_files(Path(source))
    return 0 if OK else 1


##########################################################################################
# minify
##########################################################################################
@stubber_cli.command(name="minify")
@click.option(
    "--source", "-s", default="board/createstubs.py", type=click.Path(exists=True, file_okay=True, dir_okay=False), show_default=True
)
@click.option("--target", "-t", default="./minified", type=click.Path(exists=True, file_okay=True, dir_okay=True), show_default=True)
@click.option("--diff", "-d", help="Show the functional changes made to the source script.", default=False, is_flag=True)
@click.option("--compile", "-c", "-xc", "cross_compile", help="Cross compile after minification.", default=False, is_flag=True)
@click.option("--all", "-a", help="Minify all variants (normal, _mem and _db).", default=False, is_flag=True)
@click.option(
    "--report/--no-report",
    "keep_report",
    help="Keep or disable minimal progress reporting in the minified version.",
    default=True,
    show_default=True,
)
@click.pass_context
def cli_minify(
    ctx,
    source: Union[str, Path],
    target: Union[str, Path],
    keep_report: bool,
    diff: bool,
    cross_compile: bool,
    all: bool,
) -> int:
    """
    Minify createsubs*.py.

    Creates a minified version of the SOURCE micropython file in TARGET (file or folder).
    The goal is to use less memory / not to run out of memory, while generating Firmware stubs.
    """
    if all:
        sources = ["board/createstubs.py", "board/createstubs_mem.py", "board/createstubs_db.py"]
    else:
        sources = [source]

    for source in sources:
        print(f"\nMinifying {source}...")
        result = minify(source, target, keep_report, diff, cross_compile)

    print("\nDone!")
    return 0


##########################################################################################
# get-frozen
##########################################################################################
@stubber_cli.command(name="get-frozen")
@click.option(
    "--stub-folder",
    "-stubs",
    default=config["stub-folder"],
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    show_default=True,
)
@click.option("--path", "-p", default=config["repo-folder"], type=click.Path(file_okay=False, dir_okay=True), show_default=True)
# @click.option("--micropython", "mpy_folder", default=config["mpy-folder"], type=click.Path(exists=True, file_okay=False, dir_okay=True))
# @click.option("--micropython-lib", "mpy_lib_folder", default=config["mpy-lib-folder"], type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--version", "--tag", default="", type=str, help="Version number to use. [default: Git tag]")
@click.option("--pyi/--no-pyi", default=True, help="Create .pyi files for the (new) frozen modules", show_default=True)
@click.option("--black/--no-black", default=True, help="Run black on the (new) frozen modules", show_default=True)
def cli_get_frozen(
    stub_folder: str = config["stub-folder"],
    path: str = config["repo-folder"],
    # mpy_folder: str = config["mpy-folder"],
    # mpy_lib_folder: str = config["mpy-lib-folder"],
    version: str = "",
    pyi: bool = True,
    black: bool = True,
):
    """
    Get the frozen stubs for MicroPython.

    Get the frozen modules for the checked out version of MicroPython
    """

    mpy_path = Path(path) / config["mpy-folder"]
    mpy_lib_path = Path(path) / config["mpy-lib-folder"]
    stub_paths: List[Path] = []

    if len(version) == 0:
        version = utils.clean_version(git.get_tag(mpy_path.as_posix()) or "0.0")
    if version:
        log.info("MicroPython version : {}".format(version))
        # folder/{family}-{version}-frozen
        family = "micropython"
        stub_path = Path(stub_folder) / f"{family}-{utils.clean_version(version, flat=True)}-frozen"
        stub_paths.append(stub_path)
        get_mpy.get_frozen(stub_path.as_posix(), version=version, mpy_path=mpy_path.as_posix(), lib_path=mpy_lib_path.as_posix())
    else:
        log.warning("Unable to find the micropython repo in folder : {}".format(mpy_path.as_posix()))
    utils.do_post_processing(stub_paths, pyi, black)


##########################################################################################
# get-lobo (frozen)
##########################################################################################
@stubber_cli.command(name="get-lobo")
@click.option(
    "--stub-folder",
    "-stubs",
    default=config["stub-folder"],
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    show_default=True,
)
@click.option("--pyi/--no-pyi", default=True, help="Create .pyi files for the (new) frozen modules", show_default=True)
@click.option("--black/--no-black", default=True, help="Run black on the (new) frozen modules", show_default=True)
def cli_get_lobo(
    stub_folder: str = config["stub-folder"],
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


##########################################################################################
# core
##########################################################################################


@stubber_cli.command(name="get-core")
@click.option(
    "--stub-folder",
    "-stubs",
    default=config["stub-folder"],
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    show_default=True,
)
@click.option("--pyi/--no-pyi", default=True, help="Create .pyi files for the (new) frozen modules", show_default=True)
@click.option("--black/--no-black", default=True, help="Run black on the (new) frozen modules", show_default=True)
def cli_get_core(
    stub_folder: str = config["stub-folder"],
    # core_type: str = "pycopy",  # pycopy or Micropython CPython stubs
    pyi: bool = True,
    black: bool = True,
):
    """
    Download core CPython stubs from PyPi.

    Get the core (CPython compat) modules for both MicroPython and Pycopy.
    """

    stub_paths: List[Path] = []
    for core_type in ["pycopy", "micropython"]:
        log.info(f"::group:: Get Cpython core :{core_type}")
        req_filename = f"requirements-core-{core_type}.txt"
        stub_path = Path(stub_folder) / f"cpython_core-{core_type}"

        get_cpython.get_core(stub_path=stub_path.as_posix(), requirements=req_filename, family=core_type)
        stub_paths.append(stub_path)

    utils.do_post_processing(stub_paths, pyi, black)


##########################################################################################
# get-docstubs
##########################################################################################


@stubber_cli.command(name="get-docstubs")
# todo: allow multiple source
@click.option("--path", "-p", default=config["repo-folder"], type=click.Path(file_okay=False, dir_okay=True), show_default=True)
@click.option(
    "--stub-path",
    "--stub-folder",
    "target",
    default=config["stub-folder"],
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Destination of the files to be generated.",
    show_default=True,
)
@click.option("--family", "-f", "basename", default="micropython", help="Micropython family.", show_default=True)
@click.option("--black/--no-black", "-b/-nb", default=True, help="Run black", show_default=True)
@click.option("--verbose", "-v", is_flag=True, default=False)
def cli_docstubs(
    path: str = config["repo-folder"],
    target: str = config["stub-folder"],
    verbose: bool = False,
    black: bool = True,
    basename="micropython",
):
    """
    Build stubs from documentation.

    Read the Micropython library documentation files and use them to build stubs that can be used for static typechecking.
    """
    if verbose:
        log.setLevel(logging.DEBUG)
    log.info(f"stubs_from_docs version {__version__}\n")

    if path == config["repo-folder"]:
        # default
        rst_path = Path(config["repo-folder"]) / config["mpy-folder"] / "docs" / "library"
    elif Path(path).stem == "micropython":
        # path to a micropython repo
        rst_path = Path(path) / "docs" / "library"
    else:
        rst_path = Path(path)  # or specify full path
    v_tag = git.get_tag(rst_path.as_posix())
    if not v_tag:
        # if we can't find a tag , bail
        raise ValueError
    v_tag = utils.clean_version(v_tag, flat=True, drop_v=False)
    release = git.get_tag(rst_path.as_posix(), abbreviate=False) or ""

    dst_path = Path(target) / f"{basename}-{v_tag}-docstubs"

    generate_from_rst(rst_path, dst_path, v_tag, release=release, verbose=verbose, suffix=".pyi")

    # no need to generate .pyi in post processing
    utils.do_post_processing([dst_path], False, black)


##########################################################################################
#
##########################################################################################


@stubber_cli.command(name="update-fallback")
@click.option("--version", default=RELEASED, type=str, help="Version number to use", show_default=True)
@click.option(
    "--stub-folder",
    default=config["stub-folder"],
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Destination of the files to be generated.",
    show_default=True,
)
def cli_update_fallback(
    version: str,
    stub_folder: str = config["stub-folder"],
):
    """
    Update the fallback stubs.

    The fallback stubs are updated/collated from files of the firmware-stubs, doc-stubs and core-stubs.
    """
    stub_path = Path(stub_folder)
    config = utils.config.readconfig()
    update_fallback(
        stub_path,
        stub_path / config["fallback-folder"],
        version=version,
    )


##########################################################################################

if __name__ == "__main__":
    stubber_cli()
