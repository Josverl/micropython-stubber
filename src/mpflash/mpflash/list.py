import json
from typing import List

import rich_click as click
from rich import print
from rich.progress import track
from rich.table import Table

# TODO: - refactor so that we do not need the entire stubber package
from stubber.bulk.mpremoteboard import MPRemoteBoard

from .cli_group import cli
from .config import config
from .logger import console, make_quiet


@cli.command("list", help="List the connected MCU boards.")
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
    "--progress/--no-progress",
    "progress",
    is_flag=True,
    default=True,
    show_default=True,
    help="""Show progress""",
)
def cli_list_mcus(as_json: bool, progress: bool = True):
    """List the connected MCU boards, and output in a nice table or json."""
    if as_json:
        # avoid noise in json output
        make_quiet()

    conn_mcus = list_mcus()
    if as_json:
        print(json.dumps([mcu.__dict__ for mcu in conn_mcus], indent=4))
        progress = False
    if progress:
        show_mcus(conn_mcus, refresh=False)
    return conn_mcus


def list_mcus():
    conn_mcus = [MPRemoteBoard(sp) for sp in MPRemoteBoard.connected_boards() if sp not in config.ignore_ports]

    for mcu in track(conn_mcus, description="Getting board info", transient=True, update_period=0.1):
        try:
            mcu.get_mcu_info()
        except ConnectionError as e:
            print(f"Error: {e}")
            continue
    return conn_mcus


def show_mcus(
    conn_mcus: List[MPRemoteBoard],
    title: str = "Connected boards",
    refresh: bool = True,
):
    """Show the list of connected boards in a nice table"""
    table = Table(
        title=title,
        expand=True,
        header_style="bold blue",
        collapse_padding=True,
        # row_styles=["blue", "yellow"]
    )
    table.add_column("Serial", overflow="fold")
    table.add_column("Family")
    table.add_column("Port")
    table.add_column("Board", overflow="fold")
    # table.add_column("Variant") # TODO: add variant
    table.add_column("CPU")
    table.add_column("Version", overflow="fold")
    table.add_column("build", justify="right")

    for mcu in track(conn_mcus, description="Updating board info", transient=True, update_period=0.1):
        if refresh:
            try:
                mcu.get_mcu_info()
            except ConnectionError:
                continue
        table.add_row(
            mcu.serialport,
            mcu.family,
            mcu.port,
            mcu.board if mcu.board != "UNKNOWN" else mcu.description,
            # mcu.variant,
            mcu.cpu,
            mcu.version,
            mcu.build,
        )
    console.print(table)
