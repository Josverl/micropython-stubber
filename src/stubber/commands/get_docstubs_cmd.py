"""
get-docstubs

"""

from pathlib import Path
from typing import Optional

import mpflash.basicgit as git
import rich_click as click
from mpflash.logger import log
from packaging.version import Version

import stubber.utils as utils
from stubber.codemod.enrich import enrich_folder
from stubber.commands.cli import stubber_cli
from stubber.merge_config import copy_type_modules
from stubber.modcat import CP_REFERENCE_TO_DOCSTUB
from stubber.stubs_from_docs import generate_from_rst
from stubber.utils.config import CONFIG
from stubber.utils.repos import fetch_repos

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
@click.option(
    "--autoflake/--no-autoflake",
    default=True,
    help="Run autoflake to clean imports",
    show_default=True,
)
@click.option(
    "--clean-rst/--no-clean-rst",
    default=True,
    help="remove .rST constructs from the docstrings",
    show_default=True,
)
@click.option(
    "--enrich",
    is_flag=True,
    default=False,
    help="Enrich with type information from reference/micropython",
    show_default=True,
)
# @click.option(
#     "--copy-params",
#     "copy_params",
#     default=False,
#     help="Copy the function/method parameters",
#     show_default=True,
#     is_flag=True,
# )
# @click.option(
#     "--copy-docstr",
#     "copy_docstr",
#     default=False,
#     help="Copy the docstrings",
#     show_default=False,
#     is_flag=True,
# )
@click.pass_context
def cli_docstubs(
    ctx: click.Context,
    path: Optional[str] = None,
    target: Optional[str] = None,
    black: bool = True,
    autoflake: bool = True,
    clean_rst: bool = True,
    basename: Optional[str] = None,
    version: str = "",
    enrich: bool = False,
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
    else:
        # get the current checked out version
        version = utils.checkedout_version(CONFIG.mpy_path)

    release = git.get_local_tag(rst_path.as_posix(), abbreviate=False) or ""

    dst_path = Path(target) / f"{basename}-{utils.clean_version(version, flat=True)}-docstubs"

    log.info(f"Get docstubs for MicroPython {utils.clean_version(version, drop_v=False)}")
    generate_from_rst(
        rst_path,
        dst_path,
        version,
        release=release,
        suffix=".pyi",
        black=black,
        autoflake=autoflake,
        clean_rst=clean_rst,
    )

    if enrich:
        if Version(version) < Version("1.24"):
            log.warning(f"Enriching is only supported for version v1.24+, not {version}")
        else:
            reference_path = CONFIG.stub_path.parent / "reference/micropython"
            _ = enrich_folder(
                reference_path,
                dst_path,
                show_diff=False,
                write_back=True,
                require_docstub=False,
                copy_params=True,
                copy_docstr=False,
            )
            copy_type_modules(reference_path, dst_path, CP_REFERENCE_TO_DOCSTUB)
            log.info("::group:: start post processing of retrieved stubs")
            # do not run stubgen
            utils.do_post_processing([dst_path], stubgen=False, format=black, autoflake=autoflake)

    log.info("::group:: Done")
