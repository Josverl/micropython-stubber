"""Deploy and run createstubs on one or more microcontrollers."""
##########################################################################################
# stub
##########################################################################################


import click

from stubber.bulk.mcu_stubber import stub_connected_mcus
from .cli import stubber_cli

##########################################################################################
# log = logging.getLogger("stubber")
#########################################################################################


@stubber_cli.command(name="get-mcu-stubs")
@click.option(
    "--variant",
    "-v",
    type=click.Choice(["Full", "Mem", "DB"], case_sensitive=False),
    default="DB",
    show_default=True,
    help="Variant of createstubs to run",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["py", "mpy"], case_sensitive=False),
    default="mpy",
    show_default=True,
    help="Python source or pre-compiled.",
)
@click.option("--debug/--no-debug", default=False, show_default=True, help="Debug mode.")
@click.option("--reset/--no-reset", default=False, show_default=True, help="Reset the board before running createstubs.")
@click.option("--github/--local", default=True, show_default=True, help="where to install the board files from. local is intended for development.")
def cli_create_mcu_stubs(variant: str, format: str, debug: bool, reset:bool, github:bool) -> int:
    """Run createstubs on one or more MCUs, and add the stubs to the micropython-stub repo."""
    exit(stub_connected_mcus(variant=variant, format=format, debug=debug))
