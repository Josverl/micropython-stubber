from typing import List, Tuple

from rich import print
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Column

from mpflash.common import filtered_comports
from mpflash.mpremoteboard import MPRemoteBoard


def connected_ports_boards(*, include: List[str], ignore: List[str]) -> Tuple[List[str], List[str], List[MPRemoteBoard]]:
    """
    Returns a tuple containing lists of unique ports and boards from the connected MCUs.
    Boards that are physically connected, but give no tangible response are ignored.

    Returns:
        A tuple containing three lists:
            - A list of unique ports where MCUs are connected.
            - A list of unique board names of the connected MCUs.
            - A list of MPRemoteBoard instances of the connected MCUs.
    """
    mpr_boards = [b for b in list_mcus(include=include, ignore=ignore) if b.connected]
    ports = list({b.port for b in mpr_boards})
    boards = list({b.board for b in mpr_boards})
    return (ports, boards, mpr_boards)


# #########################################################################################################
rp_spinner = SpinnerColumn(finished_text="✅")
rp_text = TextColumn("{task.description} {task.fields[device]}", table_column=Column())
rp_bar = BarColumn(bar_width=None, table_column=Column())


def list_mcus(*, ignore: List[str], include: List[str], bluetooth: bool = False) -> List[MPRemoteBoard]:
    """
    Retrieves information about connected microcontroller boards.

    Returns:
        List[MPRemoteBoard]: A list of MPRemoteBoard instances with board information.
    Raises:
        ConnectionError: If there is an error connecting to a board.
    """
    # conn_mcus = [MPRemoteBoard(sp) for sp in MPRemoteBoard.connected_boards(bluetooth) if sp not in config.ignore_ports]

    comports = filtered_comports(
        ignore=ignore,
        include=include,
        bluetooth=bluetooth,
    )
    conn_mcus = [MPRemoteBoard(c.device, location=c.location or "?") for c in comports]

    # a lot of boilerplate to show a progress bar with the comport currently scanned
    # low update rate to facilitate screen readers/narration
    with Progress(
        rp_spinner,
        rp_text,
        rp_bar,
        TimeElapsedColumn(),
        refresh_per_second=1,
    ) as progress:
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
