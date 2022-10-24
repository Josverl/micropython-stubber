"""
update-fallback folder with common set of stubs that cater for most of the devices
"""

from stubber.update_module_list import main as update_module_list

from .cli import stubber_cli


@stubber_cli.command(name="update-module-list", help="Update the module list based on the information in the data folder")
def cli_update_module_list():
    """
    Update the module list based on the information in the data folder.
    """
    update_module_list()
