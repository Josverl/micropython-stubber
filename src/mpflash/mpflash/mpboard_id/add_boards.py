"""
Collects board name and description information from MicroPython and writes it to JSON and CSV files.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import jsons
import rich
import rich.table
from rich.console import Console
from rich.progress import track

import mpflash.vendor.basicgit as git
from mpflash.vendor.versions import micropython_versions


@dataclass()
class Board:
    """MicroPython Board definition"""

    # TODO: add variant
    description: str
    board_name: str
    mcu_name: str
    port: str
    path: Path
    id: str = field(default="")  # board id
    version: str = field(default="")  # version of MicroPython""
    family: str = field(default="micropython")
    board: str = field(default="")

    def __post_init__(self):
        if self.id and self.board == "":
            self.board = self.id
        elif self.board and self.id == "":
            self.id = self.board
        elif not self.id and not self.board:
            self.id = self.board = self.description.replace(" ", "_")


# look for all mpconfigboard.h files and extract the board name
# from the #define MICROPY_HW_BOARD_NAME "PYBD_SF6"
# and the #define MICROPY_HW_MCU_NAME "STM32F767xx"
RE_H_MICROPY_HW_BOARD_NAME = re.compile(r"#define\s+MICROPY_HW_BOARD_NAME\s+\"(.+)\"")
RE_H_MICROPY_HW_MCU_NAME = re.compile(r"#define\s+MICROPY_HW_MCU_NAME\s+\"(.+)\"")
# find in the mpconfigboard.cmake files

RE_CMAKE_MICROPY_HW_BOARD_NAME = re.compile(r"MICROPY_HW_BOARD_NAME\s?=\s?\"(?P<variant>[\w\s\S]*)\"")
RE_CMAKE_MICROPY_HW_MCU_NAME = re.compile(r"MICROPY_HW_MCU_NAME\s?=\s?\"(?P<variant>[\w\s\S]*)\"")
# TODO: normal make files


def boards_from_repo(mpy_path: Path, version: str, family: Optional[str] = None) -> List[Board]:
    """Collects board name and decriptions from mpconfigboard.h files.

    Args:
        mpy_path (Path): The path to the MicroPython repository.
        version (str): The version of MicroPython.

    Returns:
        List[Board]: A list of Board objects containing the board information.
    """
    if not mpy_path.exists() or not mpy_path.is_dir():
        raise FileNotFoundError(f"MicroPython path {mpy_path} does not exist.")
    if not family:
        family = "micropython"
    if not version:
        version = git.get_local_tag()  # type: ignore
    if not version:
        raise ValueError("No version provided and no local tag found.")

    board_list: List[Board] = []
    # look in mpconfigboard.h files
    board_list = boards_from_cmake(mpy_path, version, family)

    # look for variants in the .cmake files
    board_list.extend(boards_from_headers(mpy_path, version, family))
    # TODO:? look for variants in the Makefile files

    return board_list


def boards_from_cmake(mpy_path: Path, version: str, family: str):
    """Get boards from the mpconfigboard.cmake files to the board_list."""
    board_list = []
    for path in mpy_path.glob("ports/**/mpconfigboard.cmake"):
        board = path.parent.name
        port = path.parent.parent.parent.name
        with open(path, "r") as f:
            board_name = mcu_name = "-"
            for line in f:
                line = line.strip()
                if match := RE_CMAKE_MICROPY_HW_BOARD_NAME.match(line):
                    description = match["variant"]
                    board_list.append(
                        Board(
                            id=board,
                            port=port,
                            board_name=board_name,
                            mcu_name=mcu_name,
                            description=description,
                            path=path.relative_to(mpy_path),
                            version=version,
                            family=family,
                        )
                    )
                elif match := RE_CMAKE_MICROPY_HW_MCU_NAME.match(line):
                    description = match["variant"]
                    board_list.append(
                        Board(
                            id=board,
                            port=port,
                            board_name=board_name,
                            mcu_name=mcu_name,
                            description=description,
                            path=path.relative_to(mpy_path),
                            version=version,
                            family=family,
                        )
                    )
    return board_list


def boards_from_headers(mpy_path: Path, version: str, family: str):
    """Get boards from the mpconfigboard.h files to the board_list."""
    board_list = []
    for path in mpy_path.glob("ports/**/mpconfigboard.h"):
        board = path.parent.name
        port = path.parent.parent.parent.name
        with open(path, "r") as f:
            board_name = mcu_name = "-"
            found = 0
            for line in f:
                if match := RE_H_MICROPY_HW_BOARD_NAME.match(line):
                    board_name = match[1]
                    found += 1
                elif match := RE_H_MICROPY_HW_MCU_NAME.match(line):
                    mcu_name = match[1]
                    found += 1
                if found == 2:
                    description = f"{board_name} with {mcu_name}" if mcu_name != "-" else board_name
                    board_list.append(
                        Board(
                            id=board,
                            port=port,
                            board_name=board_name,
                            mcu_name=mcu_name,
                            description=description,
                            path=path.relative_to(mpy_path),
                            version=version,
                            family=family,
                        )
                    )
                    found = 0
            if found == 1:
                description = board_name
                board_list.append(
                    Board(
                        id=board,
                        port=port,
                        board_name=board_name,
                        mcu_name=mcu_name,
                        description=description,
                        path=path.relative_to(mpy_path),
                        version=version,
                        family=family,
                    )
                )
    return board_list


def write_json(board_list: List[Board], *, folder: Path):
    """Writes the board information to JSON and CSV files.

    Args:
        board_list (List[Board]): The list of Board objects.
    """
    # write the list to json file
    with open(folder / "board_info.json", "w") as fp:
        fp.write(jsons.dumps(board_list, indent=4))

    # # create a csv with only the board and the description of the board_list
    # with open(folder / "board_info.csv", "w") as f:
    #     f.write("board,description\n")
    #     for board in board_list:
    #         f.write(f"{board.description},{board.board}\n")


def boards_for_versions(versions: List[str], mpy_path: Path):
    """Gets the list of boards for multiple versions of MicroPython.

    Args:
        versions (List[str]): The list of MicroPython versions.
        mpy_path (Path): The path to the MicroPython repository.

    Returns:
        List[Board]: The list of Board objects.
    """
    board_list: List[Board] = []
    for version in track(versions, description="Searching MicroPython versions"):
        if git.checkout_tag(tag=version, repo=mpy_path):
            new_ones = boards_from_repo(mpy_path, version, family="micropython")
            print(f"Found {len(new_ones)} board definitions for {version}.")
            board_list += new_ones
        else:
            print(f"Could not checkout version {version}.")

    # sort the board_list by description and board
    print("Total number of boards found:", len(board_list))

    board_list = unique_boards(board_list)
    print("Unique board descriptions found:", len(board_list))
    return board_list


def unique_boards(board_list):
    """Remove duplicate boards by 'description' from the list."""
    seen = set()
    board_list = [
        x for x in board_list if not (x.id + "|" + x.description in seen or seen.add(x.id + "|" + x.description))
    ]
    board_list.sort(key=lambda x: x.description.lower())
    return board_list


def make_table(board_list: List[Board]) -> rich.table.Table:
    """Creates a rich table with board information."""
    is_wide = False

    table = rich.table.Table(title="MicroPython Board Information")
    table.add_column("ID", justify="left", style="green")
    table.add_column("Description", justify="left", style="cyan")
    table.add_column("Port", justify="left", style="magenta")
    table.add_column("Board Name", justify="left", style="blue")
    if is_wide:
        table.add_column("MCU Name", justify="left", style="blue")
    table.add_column("Detection", justify="left", style="yellow")
    table.add_column("Version", justify="left", style="blue")
    if is_wide:
        table.add_column("Family", justify="left", style="blue")
        table.add_column("board", justify="left", style="blue")

    for board in board_list:
        row = [board.id, board.description, *(board.port, board.board_name)]
        if is_wide:
            row.append(board.mcu_name)
        row.extend((str(board.path.suffix), board.version))
        if is_wide:
            row.extend((board.family, board.board))
        table.add_row(*row)

    return table


def main():
    """Main function to collect and write board information."""
    console = Console()
    mpy_path = Path("D:\\MyPython\\micropython-stubber\\repos\\micropython")
    versions = micropython_versions(minver="v1.19.1") + ["master"]
    board_list = boards_for_versions(versions, mpy_path)

    table = make_table(board_list)
    console.print(table)

    write_json(board_list, folder=Path("."))
    # write_files(board_list, folder=CONFIG.board_path)


if __name__ == "__main__":
    main()
