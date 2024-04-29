from pathlib import Path
from typing import Dict, List, Optional, Tuple

from loguru import logger as log

from mpflash.common import FWInfo
from mpflash.errors import MPFlashError

from .config import config
from .downloaded import find_downloaded_firmware
from .list import show_mcus
from .mpboard_id import find_stored_board
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
    """Builds a list of boards to update based on the connected boards and the firmwares available locally in the firmware folder.

    Args:
        conn_boards (List[MPRemoteBoard]): List of connected boards
        target_version (str): Target firmware version
        fw_folder (Path): Path to the firmware folder
        selector (Optional[Dict[str, str]], optional): Selector for filtering firmware. Defaults to None.

    Returns:
        WorkList: List of boards and firmware information to update
    """
    if selector is None:
        selector = {}
    wl: WorkList = []
    for mcu in conn_boards:
        if mcu.family not in ("micropython", "unknown"):
            log.warning(
                f"Skipping flashing {mcu.family} {mcu.port} {mcu.board} on {mcu.serialport} as it is not a MicroPython firmware"
            )
            continue
        board_firmwares = find_downloaded_firmware(
            fw_folder=fw_folder,
            board_id=mcu.board,
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
    """Create a worklist for a single serial-port.

    Args:
        serial_port (str): Serial port of the board
        version (str): Firmware version
        fw_folder (Path): Path to the firmware folder

    Returns:
        WorkList: List of boards and firmware information to update
    """
    conn_boards = [MPRemoteBoard(serial_port)]
    todo = auto_update(conn_boards, version, fw_folder)  # type: ignore # List / list
    show_mcus(conn_boards)  # type: ignore
    return todo


def full_auto_worklist(*, version: str, fw_folder: Path) -> WorkList:
    """
    Create a worklist for all connected micropython boards based on the information retrieved from the board.
    This allows the firmware version of one or moae boards to be changed without needing to specify the port or board_id manually.

    Args:
        version (str): Firmware version
        fw_folder (Path): Path to the firmware folder

    Returns:
        WorkList: List of boards and firmware information to update
    """
    try:
        conn_boards = [
            MPRemoteBoard(sp, update=True) for sp in MPRemoteBoard.connected_boards() if sp not in config.ignore_ports
        ]
    except ConnectionError as e:
        log.error(f"Error connecting to boards: {e}")
        return []
    return auto_update(conn_boards, version, fw_folder)  # type: ignore


def manual_worklist(
    version: str,
    fw_folder: Path,
    serial_port: str,
    board: str,
    # port: str,
) -> WorkList:
    """Create a worklist for a single board specified manually.

    Args:
        version (str): Firmware version
        fw_folder (Path): Path to the firmware folder
        serial_port (str): Serial port of the board
        board (str): Board name

    Returns:
        WorkList: List of boards and firmware information to update
    """
    mcu = MPRemoteBoard(serial_port)
    # TODO : Find a way to avoid needing to specify the port
    # Lookup the matching port and cpu in board_info based in the board name
    try:
        info = find_stored_board(board)
        mcu.port = info["port"]
        # need the CPU type for the esptool
        mcu.cpu = info["cpu"]
    except (LookupError, MPFlashError) as e:
        log.error(f"Board {board} not found in board_info.json")
        return []
    mcu.board = board
    firmwares = find_downloaded_firmware(fw_folder=fw_folder, board_id=board, version=version, port=mcu.port)
    if not firmwares:
        log.error(f"No firmware found for {mcu.port} {board} version {version}")
        return []
        # use the most recent matching firmware
    return [(mcu, firmwares[-1])]  # type: ignore
