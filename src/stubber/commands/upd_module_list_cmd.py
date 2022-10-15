"""
update-fallback folder with common set of stubs that cater for most of the devices
"""

from pathlib import Path

import click
from stubber.update_fallback import RELEASED, update_fallback
from stubber.update_module_list import main as update_module_list
from stubber.utils.config import CONFIG

from .cli import stubber_cli


@stubber_cli.command(name="update-module-list", help="Update the module list based on the information in the data folder")
def cli_update_module_list():
    """
    Update the module list based on the information in the data folder.
    """
    update_module_list()
