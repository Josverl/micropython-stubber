"""Build stub packages - is a Light version of Publish command"""

from typing import List, Union

import rich_click as click
from mpflash.logger import log
from tabulate import tabulate

from stubber.commands.cli import stubber_cli
from stubber.publish.defaults import GENERIC_U
from stubber.publish.publish import build_multiple
from stubber.utils.config import CONFIG


@stubber_cli.command(name="build")
@click.option("--family", default="micropython", type=str, show_default=True)
@click.option(
    "--version",
    "--Version",
    "-V",
    "versions",
    multiple=True,
    default=[CONFIG.stable_version],
    show_default=True,
    help="MicroPython version to build, or 'preview' for the latest preview version",
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
    "--clean",
    is_flag=True,
    default=False,
    help="clean folders after processing and publishing",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="build package even if no changes detected",
)
def cli_build(
    family: str,
    versions: Union[str, List[str]],
    ports: Union[str, List[str]],
    boards: Union[str, List[str]],
    clean: bool,
    force: bool,
    # stub_type: str,
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

    # db = get_database(publish_path=CONFIG.publish_path, production=production)
    log.info(f"Build {family} {versions} {ports} {boards}")

    results = build_multiple(
        family=family,
        versions=versions,
        ports=ports,
        boards=boards,
        production=True,  # use production database during build
        force=force,
        clean=clean,
    )
    # log the number of results with no error
    log.info(f"Built {len([r for r in results if not r['error']])} stub packages")
    print(tabulate(results, headers="keys"))
