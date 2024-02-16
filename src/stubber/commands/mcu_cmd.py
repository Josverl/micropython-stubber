"""Deploy and run createstubs on one or more microcontrollers."""
##########################################################################################
# stub
##########################################################################################


import click

from stubber.mcu.board_stubber import run_stubber_connected_boards
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
def cli_create_mcu_stubs(variant: str, format: str, debug: bool) -> int:
    """Run createstubs on one or more MCUs, and add the stubs to the micropython-stub repo."""
    OK = run_stubber_connected_boards(variant=variant, format=format, debug=debug)
    return 0 if OK else 1
