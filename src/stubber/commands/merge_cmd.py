"""
enrich machinestubs with docstubs
"""

from typing import List, Union

import rich_click as click
from mpflash.logger import log

from stubber.commands.cli import stubber_cli
from stubber.publish.merge_docstubs import merge_all_docstubs
from stubber.publish.package import GENERIC_L
from stubber.utils.config import CONFIG


@stubber_cli.command(
    name="merge",
    aliases=["merge-stubs"],
)
@click.option("--family", default="micropython", type=str, show_default=True)
@click.option(
    "--version",
    "-v",
    "versions",
    multiple=True,
    default=["stable"],
    # type=click.Choice(ALL_VERSIONS),
    show_default=True,
    help="'stable', 'latest', 'all', or one or more versions",
)
@click.option(
    "--port",
    "-p",
    "ports",
    multiple=True,
    default=["all"],
    show_default=True,
    help="multiple: ",
)
@click.option(
    "--board",
    "-b",
    "boards",
    multiple=True,
    default=[GENERIC_L],  # or "all" ?
    show_default=True,
    help="multiple: ",
)
@click.option(
    "--clean/--no-clean",
    default=True,
    show_default=True,
    help="Clean target folders before merging.",
)
def cli_merge_docstubs(
    versions: Union[str, List[str]],
    boards: Union[str, List[str]],
    ports: Union[str, List[str]],
    family: str,
    clean: bool,
):
    """
    Enrich the stubs in stub_folder with the docstubs in docstubs_folder.
    """
    if isinstance(ports, tuple):
        ports = list(ports)
    if isinstance(boards, tuple):
        boards = list(boards)
    if isinstance(versions, tuple):
        versions = list(versions)
    # single version should be a string
    log.info(f"Merge docstubs for {family} {versions}")
    _ = merge_all_docstubs(versions=versions, family=family, boards=boards, ports=ports, clean=clean)
