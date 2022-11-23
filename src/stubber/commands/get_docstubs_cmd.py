"""
get-docstubs

"""

from pathlib import Path

import click
import stubber.basicgit as git
import stubber.utils as utils
from loguru import logger as log
from stubber.stubs_from_docs import generate_from_rst
from stubber.utils.config import CONFIG

from .cli import stubber_cli

##########################################################################################
# log = logging.getLogger("stubber")
#########################################################################################


@stubber_cli.command(name="get-docstubs")
# todo: allow multiple source
@click.option("--path", "-p", default=CONFIG.repo_path.as_posix(), type=click.Path(file_okay=False, dir_okay=True), show_default=True)
@click.option(
    "--stub-path",
    "--stub-folder",
    "target",
    default=CONFIG.stub_path.as_posix(),
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Destination of the files to be generated.",
    show_default=True,
)
@click.option("--family", "-f", "basename", default="micropython", help="Micropython family.", show_default=True)
@click.option("--black/--no-black", "-b/-nb", default=True, help="Run black", show_default=True)
@click.pass_context
def cli_docstubs(
    ctx,
    path: str = CONFIG.repo_path.as_posix(),
    target: str = CONFIG.stub_path.as_posix(),
    black: bool = True,
    basename="micropython",
):
    """
    Build stubs from documentation.

    Read the Micropython library documentation files and use them to build stubs that can be used for static typechecking.
    """

    if path == CONFIG.repo_path.as_posix():
        # default
        rst_path = CONFIG.mpy_path / "docs" / "library"
    elif Path(path).stem == "micropython":
        # path to a micropython repo
        rst_path = Path(path) / "docs" / "library"
    else:
        rst_path = Path(path)  # or specify full path
    v_tag = git.get_tag(rst_path.as_posix())
    if not v_tag:
        # if we can't find a tag , bail
        raise ValueError("No valid Tag found")
    v_tag = utils.clean_version(v_tag, flat=True, drop_v=False)
    release = git.get_tag(rst_path.as_posix(), abbreviate=False) or ""

    dst_path = Path(target) / f"{basename}-{v_tag}-docstubs"

    # get verbose from the parent context
    verbose = ctx.obj["verbose"] != 0
    log.info(f"Get docstubs for MicroPython {utils.clean_version(v_tag, drop_v=False)}")
    generate_from_rst(rst_path, dst_path, v_tag, release=release, verbose=verbose, suffix=".pyi")

    # no need to generate .pyi in post processing
    log.info(f"::group:: start post processing of retrieved stubs")
    utils.do_post_processing([dst_path], False, black)
    log.info(f"::group:: Done")
