"""
Translate board description to board designator
"""

import functools
from pathlib import Path
from typing import Optional

from mpflash.errors import MPFlashError
from mpflash.logger import log
from mpflash.mpboard_id.store import read_known_boardinfo
from mpflash.versions import clean_version, get_stable_mp_version


def find_board_id_by_description(
    descr: str,
    short_descr: str,
    *,
    version: str,
    board_info: Optional[Path] = None,
) -> Optional[str]:
    """Find the MicroPython BOARD_ID based on the description in the firmware"""

    try:
        boards = _find_board_id_by_description(
            descr=descr,
            short_descr=short_descr,
            board_info=board_info,
            version=clean_version(version) if version else None,
        )
        return boards[-1].board_id
    except MPFlashError:
        return "UNKNOWN_BOARD"


@functools.lru_cache(maxsize=20)
def _find_board_id_by_description(
    *,
    descr: str,
    short_descr: str,
    version: Optional[str] = None,
    board_info: Optional[Path] = None,
):
    """
    Find the MicroPython BOARD_ID based on the description in the firmware
    using the pre-built board_info.json file

    Parameters:
    descr: str
        Description of the board
    short_descr: str
        Short description of the board (optional)
    version: str
        Version of the MicroPython firmware
    board_info: Path
        Path to the board_info.json file (optional)

    """
    # Some functional overlap with
    # src\mpflash\mpflash\mpboard_id\__init__.py find_known_board

    candidate_boards = read_known_boardinfo(board_info)
    if not short_descr and " with " in descr:
        short_descr = descr.split(" with ")[0]
    if version:
        # filter for matching version
        if version in ("preview", "stable"):
            # match last stable
            version = get_stable_mp_version()
        known_versions = sorted({b.version for b in candidate_boards})
        if version not in known_versions:
            log.trace(f"Version {version} not found in board info, using latest known version {known_versions[-1]}")
            version = '.'.join(known_versions[-1].split('.')[:2]) # take only major.minor
        if version_matches := [b for b in candidate_boards if b.version.startswith(version)]:
            candidate_boards = version_matches
        else:
            raise MPFlashError(f"No board info found for version {version}")
    # First try full match on description, then partial match
    matches = [b for b in candidate_boards if b.description == descr]
    if not matches and short_descr:
        matches = [b for b in candidate_boards if b.description == short_descr]
    if not matches:
        # partial match (for added VARIANT)
        matches = [b for b in candidate_boards if b.description.startswith(descr)]
        if not matches and short_descr:
            matches = [b for b in candidate_boards if b.description.startswith(short_descr)]
    if not matches:
        raise MPFlashError(f"No board info found for description '{descr}' or '{short_descr}'")
    return sorted(matches, key=lambda x: x.version)

