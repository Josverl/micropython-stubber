"""
Collects board name and description information from MicroPython and writes it to JSON and CSV files.
"""

import re
from pathlib import Path
from typing import List, Optional

import inquirer
import rich
import rich.table
from rich.console import Console
from rich.progress import track

import mpflash.basicgit as git
from mpflash.logger import log
from mpflash.mpboard_id import Board
from mpflash.mpboard_id.store import write_boardinfo_json
from mpflash.versions import micropython_versions

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
                            board_id=board,
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
                            board_id=board,
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
                            board_id=board,
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
                        board_id=board,
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


def unique_boards(board_list: List[Board], *, key_version: bool = True):
    """Remove duplicate boards by 'BOARD_ID description' from the list."""
    seen = set()
    result = []
    for x in board_list:
        if key_version:
            key = f"{x.board_id}|{x.version}|{x.description}"
        else:
            key = f"{x.board_id}|{x.description}"
        if key not in seen:
            result.append(x)
            seen.add(key)
    result.sort(key=lambda x: x.description.lower())
    return result


def make_table(board_list: List[Board]) -> rich.table.Table:
    """Creates a rich table with board information."""
    is_wide = True

    table = rich.table.Table(title="MicroPython Board Information")
    table.add_column("BOARD_ID", justify="left", style="green")
    table.add_column("Description", justify="left", style="cyan")
    table.add_column("Port", justify="left", style="magenta")
    table.add_column("Board Name", justify="left", style="blue")
    if is_wide:
        table.add_column("MCU Name", justify="left", style="blue")
    table.add_column("Detection", justify="left", style="yellow")
    table.add_column("Version", justify="left", style="blue")
    if is_wide:
        table.add_column("Family", justify="left", style="blue")

    for board in board_list:
        row = [board.board_id, board.description, *(board.port, board.board_name)]
        if is_wide:
            row.append(board.mcu_name)
        row.extend((str(Path(board.path).suffix), board.version))
        if is_wide:
            row.append(board.family)
        table.add_row(*row)

    return table


def ask_mpy_path():
    """Ask the user for the path to the MicroPython repository."""
    questions = [inquirer.Text("mpy_path", message="Enter the path to the MicroPython repository", default=".\\repos\\micropython")]
    if answers := inquirer.prompt(questions):
        return Path(answers["mpy_path"])
    else:
        raise ValueError("No path provided.")


def main():
    """Main function to collect and write board information."""

    console = Console()

    mpy_path = ask_mpy_path()
    versions = micropython_versions(minver="v1.10") + ["master"]
    board_list = boards_for_versions(versions, mpy_path)

    here = Path(__file__).parent
    log.info(write_boardinfo_json(board_list, folder=here))
    # write_files(board_list, folder=CONFIG.board_path)

    # table of when the board was added
    table = make_table(unique_boards(board_list, key_version=False))
    console.print(table)


if __name__ == "__main__":
    main()
