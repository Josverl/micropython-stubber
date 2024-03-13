import json
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple, TypedDict, Union


# BoardClass based on the dataclass Board
# - scripts\get_boardnames.py
class Board(TypedDict):
    """MicroPython Board definition"""

    description: str
    port: str
    board: str
    board_name: str
    mcu_name: str
    path: Union[Path, str]
    version: str


@lru_cache(maxsize=None)
def read_boardinfo() -> List[Board]:
    with open(Path(__file__).parent / "board_info.json", "r") as file:
        return json.load(file)


def known_mp_ports() -> List[str]:
    info = read_boardinfo()
    # select the unique ports from info
    ports = set({board["port"] for board in info})
    return sorted(list(ports))


def known_mp_boards(port: str) -> List[Tuple[str, str]]:
    info = read_boardinfo()
    boards = set({(board["description"], board["board"]) for board in info if board["port"] == port})
    return sorted(list(boards))


def find_mp_port(board: str) -> str:
    info = read_boardinfo()
    for board_info in info:
        if board_info["board"] == board:
            return board_info["port"]
    return ""


if __name__ == "__main__":

    ports = known_mp_ports()
    print(ports)

    # select the unique boards from info for a specific port
    port = "stm32"
    boards = known_mp_boards(port)
    print(boards)
