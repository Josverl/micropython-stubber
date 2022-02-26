#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Pre/Post Processing for createstubs.py"""
from typing import Union
from pathlib import Path
import subprocess
import click
from .minify import minify


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
@cli.command(name="minify")
# todo: allow multiple source
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
