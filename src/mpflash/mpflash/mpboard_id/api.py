import json
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple, TypedDict, Union

from mpflash.common import PORT_FWTYPES, clean_version


# Board  based on the dataclass Board but changed to TypedDict
# - source : get_boardnames.py
class Board(TypedDict):
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
def read_boardinfo() -> List[Board]:
    """Reads the board_info.json file and returns the data as a list of Board objects"""
    with open(Path(__file__).parent / "board_info.json", "r") as file:
        return json.load(file)


def known_mp_ports() -> List[str]:
    # TODO: Filter for Version
    info = read_boardinfo()
    # select the unique ports from info
    ports = set({board["port"] for board in info if board["port"] in PORT_FWTYPES.keys()})
    return sorted(list(ports))


def known_mp_boards(port: str, versions: Optional[List[str]] = None) -> List[Tuple[str, str]]:
    """
    Returns a list of tuples with the description and board name for the given port and version

    port : str : The Micropython port to filter for
    versions : List[str] : The Micropython versions to filter for
    """
    info = read_boardinfo()
    # dont filter for 'preview' as they are not in the board_info.json
    versions = [v for v in versions if "preview" not in v] if versions else None
    if versions:
        # make sure of the v prefix
        versions = [clean_version(v) for v in versions]
        info = [board for board in info if board["version"] in versions]
    info = [board for board in info if board["port"] == port]

    boards = set({(f'{board["description"]} [{board["version"]}]', board["board"]) for board in info})
    return sorted(list(boards))


def find_mp_board(board: str) -> Board:
    """Find the board for the given board"""
    info = read_boardinfo()
    for board_info in info:
        if board_info["board"] == board:
            if "cpu" not in board_info or not board_info["cpu"]:
                if " with " in board_info["description"]:
                    board_info["cpu"] = board_info["description"].split(" with ")[-1]
                else:
                    board_info["cpu"] = board_info["port"]
            return board_info
    raise LookupError(f"Board {board} not found")
