"""
enrich machinestubs with docstubs
"""
from pathlib import Path
from typing import Union

import click
from loguru import logger as log
from stubber.codemod.enrich import enrich_folder
from stubber.utils.config import CONFIG

from .cli import stubber_cli


@stubber_cli.command(name="enrich")
@click.option(
    "--stubs",
    "-s",
    "stubs_folder",
    default=CONFIG.stub_path.as_posix(),
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="folder containing the firmware stubs to be updated",
    show_default=True,
)
@click.option(
    "--docstubs",
    "-ds",
    "docstubs_folder",
    default=CONFIG.stub_path.as_posix(),
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="folder containing the docstubs to be applied",
    show_default=True,
)
@click.option("--diff", default=False, help="Show diff", show_default=True, is_flag=True)
@click.option("--dry-run", default=False, help="Dry run does not write the files back", show_default=True, is_flag=True)
def cli_enrich_folder(
    stubs_folder: Union[str, Path],
    docstubs_folder: Union[str, Path],
    diff=False,
    dry_run=False,
):
    """
    Enrich the stubs in stub_folder with the docstubs in docstubs_folder.
    """
    write_back = not dry_run
    log.info(f"Enriching {stubs_folder} with {docstubs_folder}")
    _ = enrich_folder(Path(stubs_folder), Path(docstubs_folder), show_diff=diff, write_back=write_back, require_docstub=False)
