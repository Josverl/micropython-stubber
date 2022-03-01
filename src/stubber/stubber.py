#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Pre/Post Processing for createstubs.py"""
from typing import Union, List
from pathlib import Path
import sys
import subprocess
import click
import logging

from .minify import minify

from . import utils
from . import basicgit as git
from . import get_cpython
from . import get_mpy
from . import get_lobo
from .stubs_from_docs import generate_from_rst
from .version import __version__


##########################################################################################

STUB_FOLDER = "./all-stubs"
MPY_FOLDER = "./micropython"
MPY_LIB_FOLDER = "./micropython-lib"

log = logging.getLogger(__name__)

##########################################################################################
def do_post_processing(stub_paths: List[Path], pyi: bool, black: bool):
    "Common post processing"
    for pth in stub_paths:
        if pyi:
            log.info("Generate type hint files (pyi) in folder: {}".format(pth))
            utils.generate_pyi_files(pth)
        if black:
            try:
                cmd = ["black", "."]

                if sys.version_info.major == 3 and sys.version_info.minor <= 7:
                    # black on python 3.7 does not like some function defs
                    # def sizeof(struct, layout_type=NATIVE, /) -> int:
                    cmd += ["--fast"]
                # shell=false on ubuntu
                result = subprocess.run(cmd, capture_output=False, check=True, shell=False, cwd=pth)
                if result.returncode != 0:
                    raise Exception(result.stderr.decode("utf-8"))
            except subprocess.SubprocessError:
                log.error("some of the files are not in a proper format")


##########################################################################################
# command line interface - main group
##########################################################################################


@click.group(chain=True)
# @click.option("--debug", is_flag=True, default=False)
# TODO: add stubfolder to top level and pass using context
# @click.option("--stub-folder", "-stubs", default=STUB_FOLDER, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.pass_context
def stubber_cli(ctx, debug=False):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug


##########################################################################################
# clone
##########################################################################################
@stubber_cli.command(name="clone")
@click.option("--mpy/--no-mpy", "-m/-nm", help="clone micropython", default=True, is_flag=True)
@click.option("--mpy-lib/--no-mpy-lib", "-l/-nl", help="clone micropython-lib", default=True, is_flag=True)
@click.option("--path", "-p", default=".", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def cli_clone(mpy: bool, mpy_lib: bool, path: Union[str, Path]):
    "Clone the micropython repos locally to be able to generate frozen-stubs and doc-stubs."
    dest_path = Path(path)
    if mpy:
        git.clone(remote_repo="https://github.com/micropython/micropython.git", path=dest_path / MPY_FOLDER)
    if mpy_lib:
        git.clone(remote_repo="https://github.com/micropython/micropython-lib.git", path=dest_path / MPY_LIB_FOLDER)


##########################################################################################
# stub
##########################################################################################
@stubber_cli.command(name="stub")
@click.option("--source", "-s", type=click.Path(exists=True, file_okay=True, dir_okay=True))
def cli_stub(source: Union[str, Path]):
    "Create or update .pyi type hint files for all .py files in SOURCE path."
    log.info("Generate type hint files (pyi) in folder: {}".format(source))
    OK = utils.generate_pyi_files(Path(source))
    return 0 if OK else 1


##########################################################################################
# minify
##########################################################################################
@stubber_cli.command(name="minify")
@click.option("--source", "-s", default="board/createstubs.py", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option("--target", "-t", "-o", default="./minified", type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.option("--diff", "-d", help="Show the functional changes made to the source script.", default=False, is_flag=True)
@click.option("--compile", "-c", "-xc", "cross_compile", help="Cross compile after minification.", default=False, is_flag=True)
@click.option("--all", "-a", help="Minify all variants (normal, _mem and _db).", default=False, is_flag=True)
@click.option(
    "--report/--no-report", "keep_report", help="Keep or disable minimal progress reporting in the minified version.", default=True
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
    """Creates a minified version of the SOURCE micropython file in TARGET (file or folder)."""
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
@click.option("--stub-folder", "-stubs", default=STUB_FOLDER, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--micropython", "mpy_folder", default=MPY_FOLDER, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--micropython-lib", "mpy_lib_folder", default=MPY_LIB_FOLDER, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--version", default="", type=str, help="Version number to use. Default: Current Git tag")
@click.option("--pyi/--no-pyi", default=True, help="Create .pyi files for the (new) frozen modules")
@click.option("--black/--no-black", default=True, help="Run black on the (new) frozen modules")
def cli_get_frozen(
    stub_folder: str = STUB_FOLDER,
    mpy_folder: str = MPY_FOLDER,
    mpy_lib_folder: str = MPY_LIB_FOLDER,
    version: str = "",
    pyi: bool = True,
    black: bool = True,
):
    "Get the frozen modules for the checked out version of MicroPython"

    stub_paths: List[Path] = []

    if len(version) == 0:
        version = utils.clean_version(git.get_tag(mpy_folder) or "0.0")
    if version:
        log.info("MicroPython version : {}".format(version))
        # folder/{family}-{version}-frozen
        family = "micropython"
        stub_path = Path(stub_folder) / f"{family}-{utils.clean_version(version, flat=True)}-frozen"
        stub_paths.append(stub_path)
        get_mpy.get_frozen(stub_path.as_posix(), version=version, mpy_path=mpy_folder, lib_path=mpy_lib_folder)

    else:
        log.warning("Unable to find the micropython repo in folder : {}".format(mpy_folder))

    do_post_processing(stub_paths, pyi, black)


##########################################################################################
# get-lobo (frozen)
##########################################################################################
@stubber_cli.command(name="get-lobo")
@click.option("--stub-folder", "-stubs", default=STUB_FOLDER, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--pyi/--no-pyi", default=True, help="Create .pyi files for the (new) frozen modules")
@click.option("--black/--no-black", default=True, help="Run black on the (new) frozen modules")
def cli_get_lobo(
    stub_folder: str = STUB_FOLDER,
    pyi: bool = True,
    black: bool = True,
):
    "Get the frozen modules for the Loboris v3.2.24 fork of MicroPython"

    stub_paths: List[Path] = []

    family = "loboris"
    version = "v3.2.24"
    stub_path = Path(stub_folder) / f"{family}-{utils.clean_version(version, flat=True)}-frozen"
    stub_paths.append(stub_path)
    get_lobo.get_frozen(str(stub_path))
    stub_paths = [stub_path]

    do_post_processing(stub_paths, pyi, black)


##########################################################################################
# core
##########################################################################################


@stubber_cli.command(name="get-core")
@click.option("--stub-folder", "-stubs", default=STUB_FOLDER, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--pyi/--no-pyi", default=True, help="Create .pyi files for the (new) frozen modules")
@click.option("--black/--no-black", default=True, help="Run black on the (new) frozen modules")
def cli_get_core(
    stub_folder: str = STUB_FOLDER,
    # core_type: str = "pycopy",  # pycopy or Micropython CPython stubs
    pyi: bool = True,
    black: bool = True,
):
    "Get the core (CPython compat) modules for both MicroPython and Pycopy."

    stub_paths: List[Path] = []
    for core_type in ["pycopy", "micropython"]:
        log.info(f"::group:: Get Cpython core :{core_type}")
        req_filename = f"requirements-core-{core_type}.txt"
        stub_path = Path(stub_folder) / f"cpython_core-{core_type}"

        get_cpython.get_core(stub_path=stub_path.as_posix(), requirements=req_filename, family=core_type)
        stub_paths.append(stub_path)

    do_post_processing(stub_paths, pyi, black)


##########################################################################################
# get-docstubs
##########################################################################################


@stubber_cli.command(name="get-docstubs")
# todo: allow multiple source
@click.option(
    "--source",
    "-s",
    default=MPY_FOLDER,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Location of the MicroPython repo of folder or  folder or .rst files to proecess. Default './micropython'",
)
@click.option(
    "--stub-path",
    "--stub-folder",
    "target",
    default="./all-stubs",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Destination of the files to be generated. default : `./all-stubs/{micropython}-{version}-docstubs`.",
)
@click.option("--family", "-f", "basename", default="micropython", help="Micropython family. default:'micropython'")
@click.option("--black/--no-black", "-b/-nb", default=True, help="Run black, default :yes")
@click.option("--verbose", "-v", is_flag=True, default=False)
def cli_docstubs(
    source: str = "",
    target: str = "./all-stubs",
    verbose: bool = False,
    black: bool = True,
    basename="micropython",
):
    """Read the Micropython library documentation files and use them to build stubs that can be used for static typechecking."""
    if verbose:
        log.setLevel(logging.DEBUG)
    log.info(f"stubs_from_docs version {__version__}\n")
    if source == MPY_FOLDER:
        rst_path = Path(MPY_FOLDER) / "docs" / "library"
    else:
        rst_path = Path(source)  # or specify full path
    v_tag = git.get_tag(rst_path.as_posix())
    if not v_tag:
        # if we can't find a tag , bail
        raise ValueError
    v_tag = utils.clean_version(v_tag, flat=True, drop_v=False)
    release = git.get_tag(rst_path.as_posix(), abbreviate=False) or ""

    dst_path = Path(target) / f"{basename}-{v_tag}-docstubs"

    generate_from_rst(rst_path, dst_path, v_tag, release=release, verbose=verbose, suffix=".pyi")

    # no need to generate .pyi in post processing
    do_post_processing([dst_path], False, black)


##########################################################################################

if __name__ == "__main__":
    stubber_cli()
