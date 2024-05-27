"""
Access to the micropython port and board information that is stored in the board_info.json file 
that is included in the module.

"""

from dataclasses import dataclass
import json
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple, Union

from mpflash.common import PORT_FWTYPES
from mpflash.errors import MPFlashError
from mpflash.vendor.versions import clean_version

# KNOWN ports and boards are sourced from the micropython repo,
# this info is stored in the board_info.json file


# Board  based on the dataclass Board but changed to TypedDict
# - source : get_boardnames.py
@dataclass
class Board():
    """MicroPython Board definition"""

    description: str
    port: str
    board: str
    board_name: str
    mcu_name: str
    path: Union[Path, str]
    version: str
    cpu: str


@lru_cache(maxsize=None)
def read_known_boardinfo() -> List[Board]:
    """Reads the board_info.json file and returns the data as a list of Board objects"""
    with open(Path(__file__).parent / "board_info.json", "r") as file:
        return json.load(file)


def get_known_ports() -> List[str]:
    # TODO: Filter for Version
    mp_boards = read_known_boardinfo()
    # select the unique ports from info
    ports = set({board.port for board in mp_boards if board.port in PORT_FWTYPES.keys()})
    return sorted(list(ports))


def get_known_boards_for_port(port: Optional[str] = "", versions: Optional[List[str]] = None) -> List[Board]:
    """
    Returns a list of boards for the given port and version(s)

    port: The Micropython port to filter for
    versions:  The Micropython versions to filter for (actual versions required)"""
    mp_boards = read_known_boardinfo()

    # filter for 'preview' as they are not in the board_info.json
    # instead use stable version
    versions = versions or []
    if "preview" in versions:
        versions.remove("preview")
        versions.append("stable")
    if versions:
        # make sure of the v prefix
        versions = [clean_version(v) for v in versions]
        # filter for the version(s)
        mp_boards = [board for board in mp_boards if board.version in versions]
    # filter for the port
    if port:
        mp_boards = [board for board in mp_boards if board.port == port]
    return mp_boards


def known_stored_boards(port: str, versions: Optional[List[str]] = None) -> List[Tuple[str, str]]:
    """
    Returns a list of tuples with the description and board name for the given port and version

    port : str : The Micropython port to filter for
    versions : List[str] : The Micropython versions to filter for (actual versions required)
    """
    mp_boards = get_known_boards_for_port(port, versions)

    boards = set({(f'{board.version} {board.description}', board.board) for board in mp_boards})
    return sorted(list(boards))


@lru_cache(maxsize=20)
def find_known_board(board_id: str) -> Board:
    """Find the board for the given BOARD_ID or 'board description' and return the board info as a Board object"""
    info = read_known_boardinfo()
    for board_info in info:
        if board_id in (board_info.board, board_info.description):
            if not board_info.cpu:
                if " with " in board_info.description:
                    board_info.cpu = board_info.description.split(" with ")[-1]
                else:
                    board_info.cpu = board_info.port
            return board_info
    raise MPFlashError(f"Board {board_id} not found")
