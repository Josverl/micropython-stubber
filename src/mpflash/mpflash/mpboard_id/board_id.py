"""
Translate board description to board designator
"""

import json
from pathlib import Path
from typing import Optional

###############################################################################################
# TODO : make this a bit nicer
HERE = Path(__file__).parent
###############################################################################################


def find_board_designator(descr: str, short_descr: str, board_info: Optional[Path] = None) -> Optional[str]:
    # TODO: use the json file instead of the csv and get the cpu
    return find_board_designator_csv(descr, short_descr, board_info)


def find_board_designator_csv(descr: str, short_descr: str, board_info: Optional[Path] = None) -> Optional[str]:
    """
    Find the MicroPython BOARD designator based on the description in the firmware
    using the pre-built board_info.csv file
    """
    if not board_info:
        board_info = HERE / "board_info.csv"
    if not board_info.exists():
        raise FileNotFoundError(f"Board info file not found: {board_info}")

    short_hit = ""
    with open(board_info, "r") as file:
        while 1:
            line = file.readline()
            if not line:
                break
            descr_, board_ = line.split(",")[0].strip(), line.split(",")[1].strip()
            if descr_ == descr:
                return board_
            if short_descr and descr_ == short_descr:
                if "with" in short_descr:
                    # Good enough - no need to trawl the entire file
                    # info["board"] = board_
                    return board_
                # good enough if not found in the rest of the file (but slow)
                short_hit = board_
    return short_hit or None
