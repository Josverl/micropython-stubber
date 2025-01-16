"""
Enrich mcu/firmware stubs with information from the docstubs
"""

from pathlib import Path
from typing import Union

import rich_click as click
from mpflash.logger import log

from stubber.codemod.enrich import enrich_folder
from stubber.utils.config import CONFIG

from .cli import stubber_cli


@stubber_cli.command(name="enrich")
@click.option(
    "--dest",
    "--destination",
    "-d",
    "--stubs",
    "dest_folder",
    default=CONFIG.stub_path.as_posix(),
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    help="The destination file or folder containing the stubs stubs to be updated",
    show_default=True,
)
@click.option(
    "--source",
    "-s",
    "--docstubs",
    "source_folder",
    default=CONFIG.stub_path.as_posix(),
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    help="The source file or folder containing the docstubs to be read",
    show_default=True,
)
@click.option("--diff", default=False, help="Show diff", show_default=True, is_flag=True)
@click.option(
    "--dry-run",
    default=False,
    help="Dry run does not write the files back",
    show_default=True,
    is_flag=True,
)
@click.option(
    "--params-only",
    "params_only",
    default=False,
    help="Copy only the parameters, not the docstrings (unless the docstring is missing)",
    show_default=True,
    is_flag=True,
)
# @click.option(
#     "--package-name",
#     "-p",
#     "package_name",
#     default="",
#     help="Package name to be enriched (Optional)",
#     show_default=True,
# )
def cli_enrich_folder(
    dest_folder: Union[str, Path],
    source_folder: Union[str, Path],
    diff: bool = False,
    dry_run: bool = False,
    params_only: bool = True,
    # package_name: str = "",
):
    """
    Enrich the stubs in stub_folder with the docstubs in docstubs_folder.
    """
    write_back = not dry_run
    log.info(f"Enriching {dest_folder} with {source_folder}")
    _ = enrich_folder(
        Path(source_folder),
        Path(dest_folder),
        show_diff=diff,
        write_back=write_back,
        require_docstub=False,
        # package_name=package_name,
        params_only=params_only,
    )
