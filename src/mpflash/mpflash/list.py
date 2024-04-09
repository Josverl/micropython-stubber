from typing import List

from rich import print
from rich.progress import track
from rich.table import Table

from mpflash.mpremoteboard import MPRemoteBoard

from .config import config
from .logger import console


def list_mcus(bluetooth: bool = False):
    """
    Retrieves information about connected microcontroller boards.

    Returns:
        List[MPRemoteBoard]: A list of MPRemoteBoard instances with board information.
    Raises:
        ConnectionError: If there is an error connecting to a board.
    """
    conn_mcus = [MPRemoteBoard(sp) for sp in MPRemoteBoard.connected_boards(bluetooth) if sp not in config.ignore_ports]

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
):  # sourcery skip: extract-duplicate-method
    """Show the list of connected boards in a nice table"""
    table = Table(
        title=title,
        title_style="bold",
        header_style="bold blue",
        collapse_padding=True,
        width=110,
        row_styles=["blue", "yellow"],
    )
    table.add_column("Serial", overflow="fold")
    table.add_column("Family")
    table.add_column("Port")
    table.add_column("Board", overflow="fold")
    # table.add_column("Variant") # TODO: add variant
    table.add_column("CPU")
    table.add_column("Version")
    table.add_column("build", justify="right")

    for mcu in track(conn_mcus, description="Updating board info", transient=True, update_period=0.1):
        if refresh:
            try:
                mcu.get_mcu_info()
            except ConnectionError:
                continue
        table.add_row(
            mcu.serialport.replace("/dev/", ""),
            mcu.family,
            mcu.port,
            f"{mcu.board}\n{mcu.description}".strip(),
            # mcu.variant,
            mcu.cpu,
            mcu.version,
            mcu.build,
        )
    console.print(table)
