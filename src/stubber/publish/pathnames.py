"""
Helper functions to deal with path names and filenames for the folders in the stubs repo

"""

from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger as log

from stubber.publish.package import GENERIC, GENERIC_L
from stubber.utils.config import CONFIG
from stubber.utils.versions import clean_version

# The default board for the ports modules documented with base name only
# ESP32-GENERIC is currently hardcoded
DEFAULT_BOARDS: Dict[str, List[str]] = {
    "stm32": ["PYBV11"],
    "esp32": ["GENERIC"],
    "esp8266": ["GENERIC"],
    "rp2": ["PICO"],
    "samd": ["SEEED_WIO_TERMINAL"],
}


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
        folder_name = f"{base}-{fw['port']}"
    else:
        folder_name = f"{base}-{fw['port']}-{fw['board']}"
    # do NOT force name to lowercase
    # remove GENERIC Prefix
    folder_name = folder_name.replace("-generic_", "-").replace("-GENERIC_", "-")
    return folder_name


def get_board_path(candidate: Dict) -> Path:
    board_path = CONFIG.stub_path / board_folder_name(candidate)
    if candidate["version"] == "latest" and not board_path.exists():
        log.debug(f"no board stubs found for {candidate['version']}, trying stable")
        board_path = CONFIG.stub_path / board_folder_name(candidate, version=CONFIG.stable_version)

    return board_path


def get_merged_path(fw: Dict) -> Path:
    return CONFIG.stub_path / (board_folder_name(fw) + "-merged")
