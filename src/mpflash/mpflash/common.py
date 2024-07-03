import fnmatch
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

from github import Auth, Github
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from .logger import log

# from mpflash.mpremoteboard import MPRemoteBoard

PORT_FWTYPES = {
    "stm32": [".dfu"],  # need .dfu for pydfu.py - .hex for cube cli/GUI
    "esp32": [".bin"],
    "esp8266": [".bin"],
    "rp2": [".uf2"],
    "samd": [".uf2"],
    # below this not yet implemented / tested
    "mimxrt": [".hex"],
    "nrf": [".uf2"],
    "renesas-ra": [".hex"],
}

# Token with no permissions to avoid throttling
# https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#getting-a-higher-rate-limit
PAT_NO_ACCESS = (
    "github_pat" + "_11AAHPVFQ0qAkDnSUaMKSp" + "_ZkDl5NRRwBsUN6EYg9ahp1Dvj4FDDONnXVgimxC2EtpY7Q7BUKBoQ0Jq72X"
)
PAT = os.environ.get("GITHUB_TOKEN") or PAT_NO_ACCESS
GH_CLIENT = Github(auth=Auth.Token(PAT))


@dataclass
class FWInfo:
    """
    Downloaded Firmware information
    is somewhat related to the BOARD class in the mpboard_id module
    """

    port: str  # MicroPython port
    board: str  # MicroPython board
    filename: str = field(default="")  # relative filename of the firmware image
    firmware: str = field(default="")  # url or path to original firmware image
    variant: str = field(default="")  # MicroPython variant
    preview: bool = field(default=False)  # True if the firmware is a preview version
    version: str = field(default="")  # MicroPython version (NO v prefix)
    url: str = field(default="")  # url to the firmware image download folder
    build: str = field(default="0")  # The build = number of commits since the last release
    ext: str = field(default="")  # the file extension of the firmware
    family: str = field(default="micropython")  # The family of the firmware
    custom: bool = field(default=False)  # True if the firmware is a custom build
    description: str = field(default="")  # Description used by this firmware (custom only)

    def to_dict(self) -> dict:
        """Convert the object to a dictionary"""
        return self.__dict__

    @classmethod
    def from_dict(cls, data: dict) -> "FWInfo":
        """Create a FWInfo object from a dictionary"""
        # add missing keys
        if "ext" not in data:
            data["ext"] = Path(data["firmware"]).suffix
        if "family" not in data:
            data["family"] = "micropython"
        return cls(**data)


@dataclass
class Params:
    """Common parameters for downloading and flashing firmware"""

    ports: List[str] = field(default_factory=list)
    boards: List[str] = field(default_factory=list)
    versions: List[str] = field(default_factory=list)
    fw_folder: Path = Path()
    serial: List[str] = field(default_factory=list)
    ignore: List[str] = field(default_factory=list)


@dataclass
class DownloadParams(Params):
    """Parameters for downloading firmware"""

    clean: bool = False
    force: bool = False


class BootloaderMethod(Enum):
    AUTO = "auto"
    MANUAL = "manual"
    MPY = "mpy"
    TOUCH_1200 = "touch1200"
    NONE = "none"



@dataclass
class FlashParams(Params):
    """Parameters for flashing a board"""

    erase: bool = True
    bootloader: BootloaderMethod = BootloaderMethod.NONE
    cpu: str = ""

    def __post_init__(self):
        if isinstance(self.bootloader, str):
            self.bootloader = BootloaderMethod(self.bootloader)


ParamType = Union[DownloadParams, FlashParams]


def filtered_comports(
    ignore: Optional[List[str]] = None,
    include: Optional[List[str]] = None,
    bluetooth: bool = False,
) -> List[ListPortInfo]:  # sourcery skip: assign-if-exp
    """
    Get a list of filtered comports using the include and ignore lists.
    both can be globs (e.g. COM*) or exact port names (e.g. COM1)
    """
    if not ignore:
        ignore = []
    elif not isinstance(ignore, list):  # type: ignore
        ignore = list(ignore)
    if not include:
        include = ["*"]
    elif not isinstance(include, list):  # type: ignore
        include = list(include)

    # remove ports that are to be ignored
    log.trace(f"{include=}, {ignore=}, {bluetooth=}")
    comports = [p for p in list_ports.comports() if not any(fnmatch.fnmatch(p.device, i) for i in ignore)]
    log.trace(f"comports: {[p.device for p in comports]}")
    # remove bluetooth ports

    if include != ["*"]:
        # if there are explicit ports to include, add them to the list
        explicit = [p for p in list_ports.comports() if any(fnmatch.fnmatch(p.device, i) for i in include)]
        log.trace(f"explicit: {[p.device for p in explicit]}")
        if ignore == []:
            # if nothing to ignore, just use the explicit list as a sinple sane default
            comports = explicit
        else:
            # if there are ports to ignore, add the explicit list to the filtered list
            comports = list(set(explicit) | set(comports))
    if not bluetooth:
        # filter out bluetooth ports
        comports = [p for p in comports if "bluetooth" not in p.description.lower()]
        comports = [p for p in comports if "BTHENUM" not in p.hwid]
        if sys.platform == "darwin":
            comports = [p for p in comports if ".Bluetooth" not in p.device]
        log.trace(f"no Bluetooth: {[p.device for p in comports]}")
    log.debug(f"filtered_comports: {[p.device for p in comports]}")
    # sort
    if sys.platform == "win32":
        # Windows sort of comports by number - but fallback to device name
        return sorted(comports, key=lambda x: int(x.device.split()[0][3:]) if x.device.split()[0][3:].isdigit() else x)
    # sort by device name
    return sorted(comports, key=lambda x: x.device)
