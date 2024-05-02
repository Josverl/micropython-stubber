from typing import List

from rich import print
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, track
from rich.table import Column, Table

from mpflash.mpremoteboard import MPRemoteBoard
from mpflash.vendor.versions import clean_version

from .config import config
from .logger import console

rp_spinner = SpinnerColumn(finished_text="✅")
rp_text = TextColumn("{task.description} {task.fields[device]}", table_column=Column())
rp_bar = BarColumn(bar_width=None, table_column=Column())


def list_mcus(bluetooth: bool = False):
    """
    Retrieves information about connected microcontroller boards.

    Returns:
        List[MPRemoteBoard]: A list of MPRemoteBoard instances with board information.
    Raises:
        ConnectionError: If there is an error connecting to a board.
    """
    conn_mcus = [MPRemoteBoard(sp) for sp in MPRemoteBoard.connected_boards(bluetooth) if sp not in config.ignore_ports]

    # a lot of boilerplate to show a progress bar with the comport currenlty scanned
    with Progress(rp_spinner, rp_text, rp_bar, TimeElapsedColumn()) as progress:
        tsk_scan = progress.add_task("[green]Scanning", visible=False, total=None)
        progress.tasks[tsk_scan].fields["device"] = "..."
        progress.tasks[tsk_scan].visible = True
        progress.start_task(tsk_scan)
        try:
            for mcu in conn_mcus:
                progress.update(tsk_scan, device=mcu.serialport.replace("/dev/", ""))
                try:
                    mcu.get_mcu_info()
                except ConnectionError as e:
                    print(f"Error: {e}")
                    continue
        finally:
            # transient
            progress.stop_task(tsk_scan)
            progress.tasks[tsk_scan].visible = False
    return conn_mcus


def show_mcus(
    conn_mcus: List[MPRemoteBoard],
    title: str = "Connected boards",
    refresh: bool = True,
):
    console.print(mcu_table(conn_mcus, title, refresh))


def abbrv_family(family: str, is_wide: bool) -> str:
    ABRV = {"micropython": "upy", "circuitpython": "cpy"}
    if not is_wide:
        if family in ABRV:
            return ABRV[family]
        return family[:4]
    return family


def mcu_table(
    conn_mcus: List[MPRemoteBoard],
    title: str = "Connected boards",
    refresh: bool = True,
):
    """
    builds a rich table with the connected boards information
    The columns of the table are adjusted to the terminal width
    the columns are :
                Narrow      Wide
    - Serial    Yes         Yes
    - Family    abbrv.      Yes
    - Port      -           yes
    - Board     Yes         Yes     BOARD_ID and Description
    - CPU       -           Yes
    - Version   Yes         Yes
    - Build     *           *       only if any of the mcus have a build
    """
    table = Table(
        title=title,
        title_style="magenta",
        header_style="bold magenta",
        collapse_padding=True,
        padding=(0, 0),
    )
    # check if the terminal is wide enough to show all columns or if we need to collapse some
    is_wide = console.width > 99
    needs_build = any(mcu.build for mcu in conn_mcus)

    table.add_column("Serial" if is_wide else "Ser.", overflow="fold")
    table.add_column("Family" if is_wide else "Fam.", overflow="crop", max_width=None if is_wide else 4)
    if is_wide:
        table.add_column("Port")
    table.add_column("Board", overflow="fold")
    # table.add_column("Variant") # TODO: add variant
    if is_wide:
        table.add_column("CPU")
    table.add_column("Version", overflow="fold", min_width=5, max_width=16)
    if needs_build:
        table.add_column("Build" if is_wide else "Bld", justify="right")

    for mcu in track(conn_mcus, description="Updating board info", transient=True, update_period=0.1):
        if refresh:
            try:
                mcu.get_mcu_info()
            except ConnectionError:
                continue
        description = f"[italic bright_cyan]{mcu.description}" if mcu.description else ""
        row = [
            mcu.serialport.replace("/dev/", ""),
            abbrv_family(mcu.family, is_wide),
        ]
        if is_wide:
            row.append(mcu.port)
        row.append(f"{mcu.board}\n{description}".strip())
        if is_wide:
            row.append(mcu.cpu)
        row.append(clean_version(mcu.version))
        if needs_build:
            row.append(mcu.build)

        table.add_row(*row)
    return table
