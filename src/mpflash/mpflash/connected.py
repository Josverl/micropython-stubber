from typing import List, Tuple

from rich import print
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Column

from mpflash.common import filtered_comports
from mpflash.mpremoteboard import MPRemoteBoard

from mpflash.common import find_serial_by_path


def connected_ports_boards(
    *, include: List[str], ignore: List[str], bluetooth: bool = False
) -> Tuple[List[str], List[str], List[MPRemoteBoard]]:
    """
    Returns a tuple containing lists of unique ports and boards from the connected MCUs.
    Boards that are physically connected, but give no tangible response are ignored.

    Returns:
        A tuple containing three lists:
            - A list of unique ports where MCUs are connected.
            - A list of unique board names of the connected MCUs.
            - A list of MPRemoteBoard instances of the connected MCUs.
    """
    conn_mcus = [
        b for b in list_mcus(include=include, ignore=ignore, bluetooth=bluetooth) if b.connected
    ]
    # ignore boards that have the [micropython-stubber] ignore flag set
    conn_mcus = [
        item for item in conn_mcus if not (item.toml.get("mpflash", {}).get("ignore", False))
    ]

    ports = list({b.port for b in conn_mcus})
    boards = list({b.board for b in conn_mcus})
    return (ports, boards, conn_mcus)


# #########################################################################################################
rp_spinner = SpinnerColumn(finished_text="✅")
rp_text = TextColumn("{task.description} {task.fields[device]}", table_column=Column())
rp_bar = BarColumn(bar_width=None, table_column=Column())


def list_mcus(
    *, ignore: List[str], include: List[str], bluetooth: bool = False
) -> List[MPRemoteBoard]:
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
    connected_mcus = [
        MPRemoteBoard(
            c.device,
            location=find_serial_by_path(c.device) or c.location or c.hwid or  "?",
        )
        for c in comports
    ]

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
            for mcu in connected_mcus:
                progress.update(tsk_scan, device=mcu.serialport.replace("/dev/tty", "tty"))
                try:
                    mcu.get_mcu_info()
                except ConnectionError as e:
                    print(f"Error: {e}")
                    continue
        finally:
            # transient
            progress.stop_task(tsk_scan)
            progress.tasks[tsk_scan].visible = False
    return connected_mcus
