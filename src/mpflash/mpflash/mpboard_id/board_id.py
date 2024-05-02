"""
Translate board description to board designator
"""

import functools
import json
from pathlib import Path
from typing import Optional

from mpflash.errors import MPFlashError
from mpflash.vendor.versions import clean_version, get_stable_mp_version

###############################################################################################
HERE = Path(__file__).parent
###############################################################################################


def find_board_id_by_description(
    descr: str, short_descr: str, board_info: Optional[Path] = None, version: str = "stable"
) -> Optional[str]:
    """Find the MicroPython BOARD_ID based on the description in the firmware"""
    try:
        boards = _find_board_id_by_description(
            descr=descr,
            short_descr=short_descr,
            board_info=board_info,
            version=clean_version(version),
        )
        return boards[-1]["board"]
    except MPFlashError:
        return "UNKNOWN_BOARD"


@functools.lru_cache(maxsize=20)
def _find_board_id_by_description(
    *, descr: str, short_descr: str, version="v1.21.0", board_info: Optional[Path] = None
):
    """
    Find the MicroPython BOARD_ID based on the description in the firmware
    using the pre-built board_info.json file
    """
    if not board_info:
        board_info = HERE / "board_info.json"
    if not board_info.exists():
        raise FileNotFoundError(f"Board info file not found: {board_info}")

    info = _read_board_info(board_info)

    # filter for matching version
    if version == "preview":
        # match last stable
        version = get_stable_mp_version()
    version_matches = [b for b in info if b["version"].startswith(version)]
    if not version_matches:
        raise MPFlashError(f"No board info found for version {version}")
    matches = [b for b in version_matches if b["description"] == descr]
    if not matches and short_descr:
        matches = [b for b in version_matches if b["description"] == short_descr]
    if not matches:
        raise MPFlashError(f"No board info found for description '{descr}' or '{short_descr}'")
    return sorted(matches, key=lambda x: x["version"])


@functools.lru_cache(maxsize=20)
def _read_board_info(board_info):
    with open(board_info, "r") as file:
        info = json.load(file)
    return info
