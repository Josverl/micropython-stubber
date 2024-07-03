import json
from typing import List

import rich_click as click
from rich import print

from .cli_group import cli
from .connected import list_mcus
from .list import show_mcus
from .logger import make_quiet


@cli.command(
    "list",
    help="List the connected MCU boards. alias: devs",
    aliases=["devs"],
)
@click.option(
    "--json",
    "-j",
    "as_json",
    is_flag=True,
    default=False,
    show_default=True,
    help="""Output in json format""",
)
@click.option(
    "--serial",
    "--serial-port",
    "-s",
    "serial",
    default=["*"],
    multiple=True,
    show_default=True,
    help="Serial port(s) (or globs) to list. ",
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
@click.option(
    "--progress/--no-progress",
    # "-p/-np", -p is already used for --port
    "progress",
    is_flag=True,
    default=True,
    show_default=True,
    help="""Show progress""",
)
def cli_list_mcus(serial: List[str], ignore: List[str], bluetooth: bool, as_json: bool, progress: bool = True) -> int:
    """List the connected MCU boards, and output in a nice table or json."""
    serial = list(serial)
    ignore = list(ignore)
    if as_json:
        # avoid noise in json output
        make_quiet()
    # TODO? Ask user to select a serialport if [?] is given ?

    conn_mcus = list_mcus(ignore=ignore, include=serial, bluetooth=bluetooth)
    # ignore boards that have the [micropython-stubber] ignore flag set
    conn_mcus = [item for item in conn_mcus if not (item.toml.get("mpflash", {}).get("ignore", False))]    
    if as_json:
        # remove the path and firmware attibutes from the json output as they are always empty
        for mcu in conn_mcus:
            del mcu.path
            del mcu.firmware
        print(json.dumps([mcu.__dict__ for mcu in conn_mcus], indent=4))
        progress = False
    if progress:
        show_mcus(conn_mcus, refresh=False)
    return 0 if conn_mcus else 1
