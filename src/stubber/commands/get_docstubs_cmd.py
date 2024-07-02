"""
get-docstubs

"""

from pathlib import Path
from typing import Optional

import rich_click as click
from mpflash.logger import log

import mpflash.basicgit as git
import stubber.utils as utils
from stubber.stubs_from_docs import generate_from_rst
from stubber.utils.config import CONFIG
from stubber.utils.repos import fetch_repos

from .cli import stubber_cli

##########################################################################################
# log = logging.getLogger("stubber")
#########################################################################################


@stubber_cli.command(
    name="get-docstubs",
    aliases=["get-doc-stubs", "docstubs"],
)
@click.option(
    "--path",
    "-p",
    default=CONFIG.repo_path.as_posix(),
    type=click.Path(file_okay=False, dir_okay=True),
    show_default=True,
)
@click.option(
    "--stub-path",
    "--stub-folder",
    "target",
    default=CONFIG.stub_path.as_posix(),
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Destination of the files to be generated.",
    show_default=True,
)
#  @click.option("--family", "-f", "basename", default="micropython", help="Micropython family.", show_default=True)
@click.option(
    "--version", "--tag", default="", type=str, help="Version number to use. [default: Git tag]"
)
@click.option("--black/--no-black", "-b/-nb", default=True, help="Run black", show_default=True)
@click.pass_context
def cli_docstubs(
    ctx: click.Context,
    path: Optional[str] = None,
    target: Optional[str] = None,
    black: bool = True,
    basename: Optional[str] = None,
    version: str = "",
):
    """
    Build stubs from documentation.

    Read the Micropython library documentation files and use them to build stubs that can be used for static typechecking.
    """
    # default parameter values
    path = path or CONFIG.repo_path.as_posix()
    target = target or CONFIG.stub_path.as_posix()
    basename = basename or "micropython"

    if path == CONFIG.repo_path.as_posix():
        # default
        rst_path = CONFIG.mpy_path / "docs" / "library"
    elif Path(path).stem == "micropython":
        # path to a micropython repo
        rst_path = Path(path) / "docs" / "library"
    else:
        rst_path = Path(path)  # or specify full path

    if version:
        version = utils.clean_version(version, drop_v=False)
        result = fetch_repos(version, CONFIG.mpy_path, CONFIG.mpy_lib_path)
        if not result:
            return -1
    # get the current checked out version
    version = utils.checkedout_version(CONFIG.mpy_path)

    release = git.get_local_tag(rst_path.as_posix(), abbreviate=False) or ""

    dst_path = Path(target) / f"{basename}-{utils.clean_version(version, flat=True)}-docstubs"

    log.info(f"Get docstubs for MicroPython {utils.clean_version(version, drop_v=False)}")
    generate_from_rst(rst_path, dst_path, version, release=release, suffix=".pyi", black=black)
    log.info("::group:: Done")
