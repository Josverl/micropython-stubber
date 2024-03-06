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


@cli.command("list", help="List the connected boards.")
@click.option(
    "--json",
    "-j",
    "as_json",
    is_flag=True,
    default=False,
    show_default=True,
    help="""Output in json format""",
)
def list_boards(as_json: bool):
    conn_boards = [MPRemoteBoard(sp) for sp in MPRemoteBoard.connected_boards() if sp not in config.ignore_ports]

    for mcu in track(conn_boards, description="Getting board info"):
        try:
            mcu.get_mcu_info()
        except ConnectionError as e:
            print(f"Error: {e}")
            continue
    if as_json:
        print(json.dumps([mcu.__dict__ for mcu in conn_boards], indent=4))
    else:
        show_boards(conn_boards, refresh=False)


def show_boards(
    conn_boards: List[MPRemoteBoard],
    title: str = "Connected boards",
    refresh: bool = True,
):
    """Show the list of connected boards in a nice table"""
    table = Table(
        title=title, expand=True, header_style="bold blue", collapse_padding=True, row_styles=["blue", "yellow"]
    )
    table.add_column("Serial", overflow="fold")
    table.add_column("Family")
    table.add_column("Port")
    table.add_column("Board", overflow="fold")
    # table.add_column("Variant") # TODO: add variant
    # table.add_column("In") # TODO: add variant
    table.add_column("CPU")
    table.add_column("Version", overflow="fold")
    table.add_column("build", justify="right")

    for mcu in track(conn_boards, transient=True, description="Updating board info"):
        if refresh:
            try:
                mcu.get_mcu_info()
            except ConnectionError:
                continue
        table.add_row(
            "/dev/tty" + mcu.serialport,
            mcu.family,
            mcu.port,
            mcu.board if mcu.board != "UNKNOWN" else mcu.description,
            # mcu.variant,
            mcu.cpu,
            mcu.version,
            mcu.build,
        )
    print(table)
