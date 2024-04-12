import os
import time
from typing import TypedDict

from github import Auth, Github
from rich.progress import track

from mpflash.errors import MPFlashError
# from mpflash.mpremoteboard import MPRemoteBoard

PORT_FWTYPES = {
    "stm32": [".dfu"],  # need .dfu for pydfu.py - .hex for cube cli/GUI
    "esp32": [".bin"],
    "esp8266": [".bin"],
    "rp2": [".uf2"],
    "samd": [".uf2"],
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
