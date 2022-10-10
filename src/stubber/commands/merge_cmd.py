"""
enrich machinestubs with docstubs
"""
from typing import List, Union

import click
from loguru import logger as log
from stubber.publish.merge_docstubs import merge_all_docstubs
from stubber.utils.config import CONFIG

from .cli import stubber_cli


@stubber_cli.command(name="merge")
@click.option("--family", default="micropython", type=str, show_default=True)
@click.option(
    "--version",
    "--Version",
    "-V",
    "versions",
    multiple=True,
    default=["auto"],
    # type=click.Choice(ALL_VERSIONS),
    show_default=True,
    help="'latest', 'auto', or one or more versions",
)
def cli_merge_docstubs(
    versions: Union[str, List[str]],
    family,
):
    """
    Enrich the stubs in stub_folder with the docstubs in docstubs_folder.
    """
    # single version should be a string
    if len(versions) == 1:
        versions = versions[0]
    log.info(f"Merge docstubs for {family} {versions}")
    _ = merge_all_docstubs(versions=versions, family=family, mpy_path=CONFIG.mpy_path)
