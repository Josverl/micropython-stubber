"""
enrich machinestubs with docstubs
"""

from typing import List, Union

import rich_click as click
from mpflash.logger import log

from stubber.publish.merge_docstubs import merge_all_docstubs
from stubber.publish.package import GENERIC_L
from stubber.utils.config import CONFIG

from .cli import stubber_cli


@stubber_cli.command(name="merge")
@click.option("--family", default="micropython", type=str, show_default=True)
@click.option(
    "--version",
    "-v",
    "versions",
    multiple=True,
    default=["all"],
    # type=click.Choice(ALL_VERSIONS),
    show_default=True,
    help="'latest', 'auto', or one or more versions",
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
def cli_merge_docstubs(
    versions: Union[str, List[str]],
    boards: Union[str, List[str]],
    ports: Union[str, List[str]],
    family: str,
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
    _ = merge_all_docstubs(
        versions=versions, family=family, boards=boards, ports=ports, mpy_path=CONFIG.mpy_path
    )
