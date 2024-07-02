"""
Helper functions to deal with path names and filenames for the folders in the stubs repo

"""

from pathlib import Path
from typing import Dict, Optional

from mpflash.logger import log

from mpflash.versions import V_PREVIEW, clean_version
from stubber.publish.defaults import default_board
from stubber.publish.package import GENERIC
from stubber.utils.config import CONFIG


## Helper functions
def get_base(candidate: Dict[str, str], version: Optional[str] = None):
    if version:
        version = clean_version(version, flat=True)
    else:
        version = clean_version(candidate["version"], flat=True)
    base = f"{candidate['family']}-{version}"
    return base.lower()


def board_folder_name(fw: Dict, *, version: Optional[str] = None) -> str:
    """Return the name of the firmware folder. Can be in AnyCase."""
    base = get_base(fw, version=version)
    if fw["board"] in GENERIC:
        board = default_board(fw["port"], fw["version"])
    else:
        board = fw["board"]
    folder_name = f"{base}-{fw['port']}-{board}" if board else f"{base}-{fw['port']}"
    # do NOT force name to lowercase
    # remove GENERIC Prefix
    # folder_name = folder_name.replace("-generic_", "-").replace("-GENERIC_", "-")
    return folder_name


def get_board_path(candidate: Dict) -> Path:
    board_path = CONFIG.stub_path / board_folder_name(candidate)
    if V_PREVIEW in candidate["version"] and not board_path.exists():
        log.debug(f"no MCU stubs found for {candidate['version']}, trying stable")
        board_path = CONFIG.stub_path / board_folder_name(candidate, version=CONFIG.stable_version)

    return board_path


def get_merged_path(fw: Dict) -> Path:
    return CONFIG.stub_path / (board_folder_name(fw) + "-merged")
