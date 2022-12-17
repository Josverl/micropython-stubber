"Build stub packages - is a Light version of Publish command"
from typing import List, Union

import click
from loguru import logger as log
from stubber.commands.cli import stubber_cli
from stubber.publish.publish import publish_multiple
from tabulate import tabulate
from stubber.utils.config import CONFIG


@stubber_cli.command(name="build")
@click.option("--family", default="micropython", type=str, show_default=True)
@click.option(
    "--version",
    "--Version",
    "-V",
    "versions",
    multiple=True,
    default=[CONFIG.STABLE_VERSION],
    show_default=True,
    help="multiple: ",
)
@click.option(
    "--port",
    "-p",
    "ports",
    multiple=True,
    default=["auto"],
    show_default=True,
    help="multiple: ",
)
@click.option(
    "--board",
    "-b",
    "boards",
    multiple=True,
    default=["GENERIC"],  # or "auto" ?
    show_default=True,
    help="multiple: ",
)
@click.option(
    "--clean",
    is_flag=True,
    default=False,
    help="clean folders after processing and publishing",
)
def cli_build(
    family: str,
    versions: Union[str, List[str]],
    ports: Union[str, List[str]],
    boards: Union[str, List[str]],
    clean: bool,
    # stub_type: str,
):
    """
    Commandline interface to publish stubs.
    """
    # force overrules dryrun
    # lists please
    versions = list(versions)
    ports = list(ports)
    boards = list(boards)

    # db = get_database(publish_path=CONFIG.publish_path, production=production)
    log.info(f"Build {family} {versions} {ports} {boards}")

    results = publish_multiple(
        frozen=True,
        family=family,
        versions=versions,
        ports=ports,
        boards=boards,
        production=False,
        dryrun=True,
        force=False,
        clean=clean,
    )
    # log the number of results with no error
    log.info(f"Build {len([r for r in results if not r['error']])} stubs")
    print(tabulate(results, headers="keys"))
