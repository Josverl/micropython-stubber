"""Deploy and run createstubs on one or more microcontrollers."""

##########################################################################################
# stub
##########################################################################################


from typing import List
import rich_click as click
from mpflash.logger import log

from stubber.bulk.mcu_stubber import stub_connected_mcus
from stubber.utils.config import CONFIG

from .cli import stubber_cli

##########################################################################################
# log = logging.getLogger("stubber")
#########################################################################################


@stubber_cli.command(
    name="get-mcu-stubs",
    aliases=["get-mcu-stubs", "mcu-stubs", "mcu"],
)
@click.option(
    "--variant",
    # "-v",
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
@click.option(
    "--serial",
    "--serial-port",
    "-s",
    "serial",
    default=["*"],
    multiple=True,
    show_default=True,
    help="Which serial port(s) (or globs) to list. ",
    metavar="SERIALPORT",
)
@click.option(
    "--ignore",
    "-i",
    is_eager=True,
    help="Serial port(s) (or globs) to ignore. Defaults to MPFLASH_IGNORE.",
    multiple=True,
    default=[],
    envvar="MPFLASH_IGNORE",
    show_default=True,
    metavar="SERIALPORT",
)
@click.option(
    "--bluetooth/--no-bluetooth",
    "-b/-nb",
    is_flag=True,
    default=False,
    show_default=True,
    help="""Include bluetooth ports in the list""",
)
@click.option("--debug/--no-debug", default=False, show_default=True, help="Debug mode.")
def cli_create_mcu_stubs(
    variant: str,
    format: str,
    debug: bool,
    serial: List[str],
    ignore: List[str],
    bluetooth: bool,
) -> int:
    """Run createstubs on one or more MCUs, and add the stubs to the micropython-stub repo."""
    # check if all repos have been cloned
    serial = list(serial)
    ignore = list(ignore)

    for repo in CONFIG.repos:
        if not repo.exists():
            log.error(
                f"Repo {repo} not found, use 'stubber clone --add-stubs' to clone the repos."
            )
            exit(1)

    exit(
        stub_connected_mcus(
            variant=variant,
            format=format,
            debug=debug,
            serial=serial,
            ignore=ignore,
            bluetooth=bluetooth,
        )
    )
