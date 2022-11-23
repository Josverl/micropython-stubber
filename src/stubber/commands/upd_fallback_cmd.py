"""
update-fallback folder with common set of stubs that cater for most of the devices
"""

import click
from pathlib import Path
from stubber.update_fallback import update_fallback, RELEASED
from stubber.utils.config import CONFIG

from .cli import stubber_cli


@stubber_cli.command(name="update-fallback")
@click.option("--version", default=RELEASED, type=str, help="Version number to use", show_default=True)
@click.option(
    "--stub-folder",
    default=CONFIG.stub_path.as_posix(),
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Destination of the files to be generated.",
    show_default=True,
)
def cli_update_fallback(
    version: str,
    stub_folder: str = CONFIG.stub_path.as_posix(),
):
    """
    Update the fallback stubs.

    The fallback stubs are updated/collated from files of the firmware-stubs, doc-stubs and core-stubs.
    """
    stub_path = Path(stub_folder)
    update_fallback(
        stub_path,
        CONFIG.fallback_path,
        version=version,
    )
