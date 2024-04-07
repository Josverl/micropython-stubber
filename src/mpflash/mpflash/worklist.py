from pathlib import Path
from typing import Dict, List, Optional, Tuple

from loguru import logger as log

from mpflash.common import FWInfo

from .config import config
from .downloaded import find_downloaded_firmware
from .mpboard_id.api import find_stored_board
from .mpremoteboard import MPRemoteBoard

# #########################################################################################################
WorkList = List[Tuple[MPRemoteBoard, FWInfo]]
# #########################################################################################################


def auto_update(
    conn_boards: List[MPRemoteBoard],
    target_version: str,
    fw_folder: Path,
    *,
    selector: Optional[Dict[str, str]] = None,
) -> WorkList:
    """Builds a list of boards to update based on the connected boards and the firmware available"""
    if selector is None:
        selector = {}
    wl: WorkList = []
    for mcu in conn_boards:
        if mcu.family != "micropython":
            log.warning(
                f"Skipping {mcu.family} {mcu.port} {mcu.board} on {mcu.serialport} as it is a MicroPython firmware"
            )
            continue
        board_firmwares = find_downloaded_firmware(
            fw_folder=fw_folder,
            board=mcu.board,
            version=target_version,
            port=mcu.port,
            selector=selector,
        )

        if not board_firmwares:
            log.error(f"No {target_version} firmware found for {mcu.board} on {mcu.serialport}.")
            continue
        if len(board_firmwares) > 1:
            log.debug(f"Multiple {target_version} firmwares found for {mcu.board} on {mcu.serialport}.")

        # just use the last firmware
        fw_info = board_firmwares[-1]
        log.info(f"Found {target_version} firmware {fw_info['filename']} for {mcu.board} on {mcu.serialport}.")
        wl.append((mcu, fw_info))
    return wl


def single_auto_worklist(
    *,
    serial_port: str,
    version: str,
    fw_folder: Path,
) -> WorkList:
    """Create a worklist for a single serial-port."""
    conn_boards = [MPRemoteBoard(serial_port)]
    todo = auto_update(conn_boards, version, fw_folder)  # type: ignore # List / list
    show_mcus(conn_boards)  # type: ignore
    return todo


def full_auto_worklist(*, version: str, fw_folder: Path) -> WorkList:
    conn_boards = [
        MPRemoteBoard(sp, update=True) for sp in MPRemoteBoard.connected_boards() if sp not in config.ignore_ports
    ]
    return auto_update(conn_boards, version, fw_folder)  # type: ignore


def manual_worklist(
    version: str,
    fw_folder: Path,
    serial_port: str,
    board: str,
    # port: str,
) -> WorkList:
    mcu = MPRemoteBoard(serial_port)
    # TODO : Find a way to avoid needing to specify the port
    # Lookup the matching port and cpu in board_info based in the board name
    try:
        port = find_stored_board(board)["port"]
    except LookupError:
        log.error(f"Board {board} not found in board_info.json")
        return []
    mcu.port = port
    mcu.cpu = port if port.startswith("esp") else ""
    mcu.board = board
    firmwares = find_downloaded_firmware(fw_folder=fw_folder, board=board, version=version, port=port)
    if not firmwares:
        log.error(f"No firmware found for {port} {board} version {version}")
        return []
        # use the most recent matching firmware
    return [(mcu, firmwares[-1])]  # type: ignore
