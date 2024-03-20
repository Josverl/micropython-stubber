"""
Collects board name and description information from MicroPython and writes it to JSON and CSV files.
"""

import json
import re
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import List

from loguru import logger as log
from tabulate import tabulate

import stubber.basicgit as git
from mpflash.common import micropython_versions


@dataclass()
class Board:
    """MicroPython Board definition"""

    description: str
    port: str
    board: str
    board_name: str
    mcu_name: str
    path: Path
    version: str = ""


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o: object):
        if is_dataclass(o):
            return asdict(o)  # type: ignore
        elif isinstance(o, Path):
            return o.as_posix()
        return super().default(o)


# look for all mpconfigboard.h files and extract the board name
# from the #define MICROPY_HW_BOARD_NAME "PYBD_SF6"
# and the #define MICROPY_HW_MCU_NAME "STM32F767xx"


RE_BOARD_NAME = re.compile(r"#define\s+MICROPY_HW_BOARD_NAME\s+\"(.+)\"")
RE_MCU_NAME = re.compile(r"#define\s+MICROPY_HW_MCU_NAME\s+\"(.+)\"")
RE_CMAKE_BOARD_NAME = re.compile(r"MICROPY_HW_BOARD_NAME\s?=\s?\"(?P<variant>[\w\s\S]*)\"")
RE_CMAKE_MCU_NAME = re.compile(r"MICROPY_HW_MCU_NAME\s?=\s?\"(?P<variant>[\w\s\S]*)\"")
# TODO: normal make files


def collect_boardinfo(mpy_path: Path, version: str) -> List[Board]:
    """Collects board name and decriptions from mpconfigboard.h files.

    Args:
        mpy_path (Path): The path to the MicroPython repository.
        version (str): The version of MicroPython.

    Returns:
        List[Board]: A list of Board objects containing the board information.
    """
    board_list: List[Board] = []
    # look in boards
    for path in mpy_path.glob("ports/**/mpconfigboard.h"):
        board = path.parent.name
        port = path.parent.parent.parent.name
        with open(path, "r") as f:
            board_name = mcu_name = "-"
            found = 0
            for line in f:
                if match := RE_BOARD_NAME.match(line):
                    board_name = match[1]
                    found += 1
                elif match := RE_MCU_NAME.match(line):
                    mcu_name = match[1]
                    found += 1
                if found == 2:
                    description = f"{board_name} with {mcu_name}" if mcu_name != "-" else board_name
                    board_list.append(
                        Board(
                            port=port,
                            board=board,
                            board_name=board_name,
                            mcu_name=mcu_name,
                            description=description,
                            path=path.relative_to(mpy_path),
                            version=version,
                        )
                    )
                    found = 0
            if found == 1:
                description = board_name
                board_list.append(
                    Board(
                        port=port,
                        board=board,
                        board_name=board_name,
                        mcu_name=mcu_name,
                        description=description,
                        path=path.relative_to(mpy_path),
                        version=version,
                    )
                )
    # look for variants in the .cmake files
    for path in mpy_path.glob("ports/**/mpconfigboard.cmake"):
        board = path.parent.name
        port = path.parent.parent.parent.name
        with open(path, "r") as f:
            board_name = mcu_name = "-"
            found = 0
            for line in f:
                line = line.strip()
                if match := RE_CMAKE_BOARD_NAME.match(line):
                    description = match["variant"]
                    board_list.append(
                        Board(
                            port=port,
                            board=board,
                            board_name=board_name,
                            mcu_name=mcu_name,
                            description=description,
                            path=path.relative_to(mpy_path),
                            version=version,
                        )
                    )
                elif match := RE_CMAKE_MCU_NAME.match(line):
                    description = match["variant"]
                    board_list.append(
                        Board(
                            port=port,
                            board=board,
                            board_name=board_name,
                            mcu_name=mcu_name,
                            description=description,
                            path=path.relative_to(mpy_path),
                            version=version,
                        )
                    )

    # look for variants in the Makefile files

    return board_list


def write_files(board_list: List[Board], *, folder: Path):
    """Writes the board information to JSON and CSV files.

    Args:
        board_list (List[Board]): The list of Board objects.
    """
    # write the list to json file
    with open(folder / "board_info.json", "w") as f:
        json.dump(board_list, f, indent=4, cls=EnhancedJSONEncoder)

    # create a csv with only the board and the description of the board_list
    with open(folder / "board_info.csv", "w") as f:
        f.write("board,description\n")
        for board in board_list:
            f.write(f"{board.description},{board.board}\n")


def get_board_list(versions: List[str], mpy_path: Path):
    """Gets the list of boards for multiple versions of MicroPython.

    Args:
        versions (List[str]): The list of MicroPython versions.
        mpy_path (Path): The path to the MicroPython repository.

    Returns:
        List[Board]: The list of Board objects.
    """
    board_list: List[Board] = []
    for version in versions:
        print(git.checkout_tag(tag=version, repo=mpy_path))
        new_ones = collect_boardinfo(mpy_path, version)
        print(f"Found {len(new_ones)} board definitions for {version}.")
        board_list += new_ones

    # sort the board_list by description and board
    print("Total number of boards found:", len(board_list))
    seen = set()
    board_list = [x for x in board_list if not (x.description in seen or seen.add(x.description))]
    board_list.sort(key=lambda x: x.description.lower())
    print("Unique board descriptions found:", len(board_list))
    return board_list


def main():
    """Main function to collect and write board information."""
    mpy_path = Path("repos/micropython")

    versions = micropython_versions(minver="v1.10")
    if not versions:
        log.error("No versions found")
        return 1
    versions.reverse()
    board_list = get_board_list(versions, mpy_path)

    print(tabulate(board_list, headers="keys"))  # type: ignore
    write_files(board_list, folder=Path(__file__).parent)
    write_files(board_list, folder=Path(__file__).parent)


if __name__ == "__main__":
    main()
