from dataclasses import dataclass, is_dataclass, asdict

from pathlib import Path
import re
from typing import List
from tabulate import tabulate
import json


@dataclass
class Board:
    """MicroPython Board definition"""

    port: str
    board: str
    board_name: str
    mcu_name: str
    description: str
    path: Path


# look for all mpconfigboard.h files and extract the board name
# from the #define MICROPY_HW_BOARD_NAME "PYBD_SF6"
# and the #define MICROPY_HW_MCU_NAME "STM32F767xx"

mpy_path = Path("repos/micropython")
re_board_name = re.compile(r"#define MICROPY_HW_BOARD_NAME\s+\"(.+)\"")
re_mcu_name = re.compile(r"#define MICROPY_HW_MCU_NAME\s+\"(.+)\"")


board_list: List[Board] = []

for path in mpy_path.glob("**/mpconfigboard.h"):
    board = path.parent.name
    port = path.parent.parent.parent.name
    with open(path, "r") as f:
        board_name = mcu_name = "-"
        found = 0
        for line in f:
            if match := re_board_name.match(line):
                board_name = match[1]
                found += 1
            elif match := re_mcu_name.match(line):
                mcu_name = match[1]
                found += 1
            if found == 2:
                break
    description = f"{board_name} with {mcu_name}" if mcu_name != "-" else board_name
    board_list.append(Board(port, board, board_name, mcu_name, description, path))

print(f"Found {len(board_list)} board definitions.")

print(tabulate(board_list, headers="keys")) # type: ignore


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        elif isinstance(o, Path):
            return o.as_posix()
        return super().default(o)


# write the list to json file
with open("src/stubber/data/board_info.json", "w") as f:
    json.dump(board_list, f, indent=4, cls=EnhancedJSONEncoder)

# create a csv with only the board and the description of the board_list
with open("src/stubber/data/board_info.csv", "w") as f:
    f.write("board,description\n")
    for board in board_list:
        f.write(f"{board.description},{board.board}\n")
