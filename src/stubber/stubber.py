#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Pre/Post Processing for createstubs.py"""
from typing import Union
from pathlib import Path
import click
import logging

from .minify import minify
from .utils import generate_pyi_files
from .basicgit import clone

log = logging.getLogger(__name__)

##########################################################################################
# command line interface
##########################################################################################


@click.group()
# @click.option("--debug", is_flag=True, default=False)
@click.pass_context
def cli(ctx, debug=False):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug


##########################################################################################


# @cli.command()  # @cli, not @click!
# @click.pass_context
# def sync(ctx):
#     click.echo(f"Debug is {'on' if ctx.obj['DEBUG'] else 'off'}")
#     click.echo("Syncing")

##########################################################################################
# stub
##########################################################################################
@cli.command(name="init")
@click.option("--mpy/--no-mpy", "-m/-nm", help="clone micropython", default=True, is_flag=True)
@click.option("--mpy-lib/--no-mpy-lib", "-l/-nl", help="clone micropython-lib", default=True, is_flag=True)
@click.option("--path", "-p", default=".", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def cli_init(mpy: bool, mpy_lib: bool, path: Union[str, Path]):
    "clone the micropython repos locally to generate frozen- and doc-stubs"
    dest_path = Path(path)
    if mpy:
        clone(remote_repo="https://github.com/micropython/micropython.git", path=dest_path / "micropython")
    if mpy_lib:
        clone(remote_repo="https://github.com/micropython/micropython-lib.git", path=dest_path / "micropython-lib")


##########################################################################################
# stub
##########################################################################################
@cli.command(name="stub")
@click.option("--source", "-s", type=click.Path(exists=True, file_okay=True, dir_okay=True))
def cli_stub(source: Union[str, Path]):
    "Generate or update type hint files for all files in SOURCE"
    log.info("Generate type hint files (pyi) in folder: {}".format(source))
    OK = generate_pyi_files(Path(source))
    return 0 if OK else 1


##########################################################################################
# minify
##########################################################################################
@cli.command(name="minify")
@click.option("--source", "-s", default="board/createstubs.py", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option("--target", "-t", "-o", default="./minified", type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.option("--diff", "-d", help="show the functional changes made to the source script", default=False, is_flag=True)
@click.option("--compile", "-c", "-xc", "cross_compile", help="cross compile after minification", default=False, is_flag=True)
@click.option("--all", "-a", help="minify all variants (normal, _mem and _db)", default=False, is_flag=True)
@click.option(
    "--report/--no-report", "keep_report", help="keep or disable minimal progress reporting in the minified version.", default=True
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
    """minifies SOURCE micropython file to TARGET (file or folder)"""
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

if __name__ == "__main__":
    cli()
