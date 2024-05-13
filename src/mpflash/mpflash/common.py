import fnmatch
import os
import sys
from typing import List, Optional, TypedDict

from github import Auth, Github
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from mpflash.errors import MPFlashError

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


class FWInfo(TypedDict):
    filename: str
    port: str
    board: str
    variant: str
    preview: bool
    version: str
    build: str


def filtered_comports(
    ignore: Optional[List[str]] = None,
    include: Optional[List[str]] = None,
    bluetooth: bool = False,
) -> List[ListPortInfo]:  # sourcery skip: assign-if-exp
    """
    Get a list of filtered comports.
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
    return comports
