"""
Commandline interface to publish stubs.
"""

from typing import List, Union

import rich_click as click
from mpflash.logger import log
from rich.console import Console
from rich.table import Table

from stubber.commands.cli import stubber_cli
from stubber.publish.defaults import GENERIC_U
from stubber.publish.publish import publish_multiple
from stubber.utils.config import CONFIG


@stubber_cli.command(name="publish")
@click.option("--family", default="micropython", type=str, show_default=True)
@click.option(
    "--version",
    "-v",
    "versions",
    multiple=True,
    default=[CONFIG.stable_version],
    show_default=True,
    help="multiple: ",
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
    default=[GENERIC_U],  # or "all" ?
    show_default=True,
    help="multiple: ",
)
@click.option(
    "--pypi/--test-pypi",
    "production",
    is_flag=True,
    default=False,
    show_default=True,
    prompt="Publish to PYPI (y) or Test-PYPI (n)",
    help="publish to PYPI or Test-PYPI",
)
@click.option(
    "--build",
    is_flag=True,
    default=False,
    help="build before publish",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="create new post release even if no changes detected",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Do not actually publish, just show what would be done",
)
@click.option(
    "--clean",
    is_flag=True,
    default=False,
    help="clean folders after processing and publishing",
)
def cli_publish(
    family: str,
    versions: Union[str, List[str]],
    ports: Union[str, List[str]],
    boards: Union[str, List[str]],
    production: bool = False,
    build: bool = False,
    force: bool = False,
    dry_run: bool = False,
    clean: bool = False,
):
    """
    Commandline interface to publish stubs.
    """
    # lists please
    versions = list(versions)
    ports = list(ports)
    boards = list(boards)

    if len(versions) > 1:
        raise NotImplementedError(
            "Multiple versions are not supported yet\n See https://github.com/Josverl/micropython-stubber/issues/487"
        )

    destination = "pypi" if production else "test-pypi"
    log.info(f"Publish {family} {versions} {ports} {boards} to {destination}")

    results = publish_multiple(
        family=family,
        versions=versions,
        ports=ports,
        boards=boards,
        production=production,
        build=build,
        force=force,
        dry_run=dry_run,
        clean=clean,
    )
    console = Console()

    if not results:
        console.print("No results to publish")
        return

    table = Table(show_header=True, header_style="bold magenta", title="Publish Results")
    headers = results[0].keys()
    for header in headers:
        table.add_column(header)

    for result in results:
        if result["result"] != "-":
            table.add_row(*[str(result[header]) for header in headers])

    console.print(table)
