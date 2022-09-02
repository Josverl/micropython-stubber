import logging
from pathlib import Path
from typing import List, Union

import click
from stubber.publish.database import get_database
from stubber.publish.enums import ALL_TYPES
from stubber.publish.publish import publish, publish_multiple
from stubber.utils.config import CONFIG
from stubber.utils.my_version import __version__

from .stubber_cli import stubber_cli

##########################################################################################
log = logging.getLogger("stubber")
###########

# TODO: make the VERSION AND PORTS dynamic ( move into simpler Config class)
LAST_VERSION = "1.19.1"
ALL_VERSIONS = ["1.17", "1.18", "1.19", "1.19.1"]  # "1.14", "1.15", "1.16","1.17",
ALL_PORTS = ["stm32", "esp32", "esp8266", "rp2"]
ALL_BOARDS = ["GENERIC"]


@stubber_cli.command(name="publish")
@click.option("--family", default="micropython", type=str, show_default=True)
@click.option(
    "--version",
    "--Version",
    "-V",
    "versions",
    multiple=True,
    default=[LAST_VERSION],
    # type=click.Choice(ALL_VERSIONS),
    show_default=True,
    help="multiple: ",
)
@click.option(
    "--port",
    "-p",
    "ports",
    multiple=True,
    default=ALL_PORTS,
    type=click.Choice(ALL_PORTS),
    show_default=True,
    help="multiple: ",
)
@click.option(
    "--board",
    "-b",
    "boards",
    multiple=True,
    default=ALL_BOARDS,
    type=click.Choice(ALL_BOARDS),
    show_default=True,
    help="multiple: ",
)
@click.option(
    "--pypi/--test-pypi",
    "production",
    is_flag=True,
    default=False,
    prompt="Publish to PYPI (y) or Test-PYPI (n)",
    help="publish to PYPI or Test-PYPI",
)
@click.option(
    "--dry-run",
    "dryrun",
    is_flag=True,
    default=False,
    help="go though the motions but do not publish",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="create new post release even if no changes detected",
)
@click.option(
    "--clean",
    is_flag=True,
    default=False,
    help="clean folders after processing and publishing",
)
@click.option(
    "--type",
    "-t",
    "stub_type",
    default=ALL_TYPES[0],
    type=click.Choice(ALL_TYPES),
    help="stub type to publish",
)
@click.option("-v", "--verbose", count=True)
#
def cli_publish(
    family: str,
    versions: Union[str, List[str]],
    ports: Union[str, List[str]],
    boards: Union[str, List[str]],
    production: bool,
    dryrun: bool,
    force: bool,
    verbose,
    clean: bool,
    stub_type: str,
):
    """
    Commandline interface to publish stubs.
    """
    # force overrules dryrun
    if force:
        dryrun = False
    # lists please
    versions = list(versions)
    ports = list(ports)
    boards = list(boards)

    root_path: Path = Path("./publish")
    root_path: Path = Path("/develop/MyPython/micropython-stubs")

    db = get_database(root_path=root_path, production=False)

    # if stub_type == "combo":
    #     publish_combo_stubs(
    #         versions=versions,
    #         ports=ports,
    #         boards=boards,
    #         db=db,
    #         pub_path=root_path / "publish",
    #         family=family,
    #         production=production,
    #         dryrun=dryrun,
    #         clean=clean,
    #     )
    # elif stub_type == "doc":
    #     publish_doc_stubs(
    #         versions=versions,
    #         db=db,
    #         pub_path=root_path / "publish",
    #         family=family,
    #         production=production,
    #         dryrun=dryrun,
    #         clean=clean,
    #     )
    #     pass
    # # elif stub_type == "core":
    # #     pass
    # else:
    #     log.warning("unknown stub type :", stub_type)
    #     raise ValueError
