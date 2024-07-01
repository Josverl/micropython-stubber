"""
Access to the micropython port and board information that is stored in the board_info.json file 
that is included in the module.

"""

from functools import lru_cache
from typing import List, Optional, Tuple

from mpflash.errors import MPFlashError
from mpflash.mpboard_id.board import Board
from mpflash.mpboard_id.store import read_known_boardinfo
from mpflash.versions import clean_version

# KNOWN ports and boards are sourced from the micropython repo,
# this info is stored in the board_info.json file


def get_known_ports() -> List[str]:
    # TODO: Filter for Version
    mp_boards = read_known_boardinfo()
    # select the unique ports from info
    ports = set({board.port for board in mp_boards if board.port})
    return sorted(list(ports))


def get_known_boards_for_port(port: Optional[str] = "", versions: Optional[List[str]] = None) -> List[Board]:
    """
    Returns a list of boards for the given port and version(s)

    port: The Micropython port to filter for
    versions:  Optional, The Micropython versions to filter for (actual versions required)
    """
    mp_boards = read_known_boardinfo()
    if versions:
        preview_or_stable = "preview" in versions or "stable" in versions
    else:
        preview_or_stable = False

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
        if not mp_boards and preview_or_stable:
            # nothing found - perhaps there is a newer version for which we do not have the board info yet
            # use the latest known version from the board info
            mp_boards = read_known_boardinfo()
            last_known_version = sorted({b.version for b in mp_boards})[-1]
            mp_boards = [board for board in mp_boards if board.version == last_known_version]

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

    boards = set({(f"{board.version} {board.description}", board.board_id) for board in mp_boards})
    return sorted(list(boards))


@lru_cache(maxsize=20)
def find_known_board(board_id: str) -> Board:
    """Find the board for the given BOARD_ID or 'board description' and return the board info as a Board object"""
    # FIXME : functional overlap with:
    # mpboard_id\board_id.py _find_board_id_by_description
    info = read_known_boardinfo()
    for board_info in info:
        if board_id in (board_info.board_id, board_info.description):
            if not board_info.cpu:
                # safeguard for older board_info.json files
                print(f"Board {board_id} has no CPU info, using port as CPU")
                if " with " in board_info.description:
                    board_info.cpu = board_info.description.split(" with ")[-1]
                else:
                    board_info.cpu = board_info.port
            return board_info
    raise MPFlashError(f"Board {board_id} not found")
