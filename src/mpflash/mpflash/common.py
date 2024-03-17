import os
import time
from typing import TypedDict

from github import Auth, Github
from loguru import logger as log
from packaging.version import parse
from rich.progress import track

from mpflash.mpremoteboard import MPRemoteBoard

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


#############################################################
# Version handling copied from stubber/utils/versions.py
#############################################################
V_PREVIEW = "preview"
"Latest preview version"

SET_PREVIEW = {"preview", "latest", "master"}


def clean_version(
    version: str,
    *,
    build: bool = False,
    patch: bool = False,
    commit: bool = False,
    drop_v: bool = False,
    flat: bool = False,
):
    "Clean up and transform the many flavours of versions"
    # 'v1.13.0-103-gb137d064e' --> 'v1.13-103'
    if version in {"", "-"}:
        return version
    if version.lower() == "stable":
        _v = get_stable_version()
        if not _v:
            log.warning("Could not determine the latest stable version")
            return "stable"
        version = _v
        log.info(f"Using latest stable version: {version}")
    is_preview = "-preview" in version
    nibbles = version.split("-")
    ver_ = nibbles[0].lower().lstrip("v")
    if not patch and ver_ >= "1.10.0" and ver_ < "1.20.0" and ver_.endswith(".0"):
        # remove the last ".0" - but only for versions between 1.10 and 1.20 (because)
        nibbles[0] = nibbles[0][:-2]
    if len(nibbles) == 1:
        version = nibbles[0]
    elif build and not is_preview:
        version = "-".join(nibbles) if commit else "-".join(nibbles[:-1])
    else:
        # version = "-".join((nibbles[0], LATEST))
        # HACK: this is not always right, but good enough most of the time
        if is_preview:
            version = "-".join((nibbles[0], V_PREVIEW))
        else:
            version = V_PREVIEW
    if flat:
        version = version.strip().replace(".", "_").replace("-", "_")
    else:
        version = version.strip().replace("_preview", "-preview").replace("_", ".")

    if drop_v:
        version = version.lstrip("v")
    elif not version.startswith("v") and version.lower() not in SET_PREVIEW:
        version = "v" + version
    if version in SET_PREVIEW:
        version = V_PREVIEW
    return version


def micropython_versions(minver: str = "v1.10"):
    """Get the list of micropython versions from github tags"""
    try:
        gh_client = GH_CLIENT
        repo = gh_client.get_repo("micropython/micropython")
        versions = [tag.name for tag in repo.get_tags() if parse(tag.name) >= parse(minver)]
    except Exception:
        versions = [
            "v9.99.9-preview",
            "v1.22.2",
            "v1.22.1",
            "v1.22.0",
            "v1.21.1",
            "v1.21.0",
            "v1.20.0",
            "v1.19.1",
            "v1.19",
            "v1.18",
            "v1.17",
            "v1.16",
            "v1.15",
            "v1.14",
            "v1.13",
            "v1.12",
            "v1.11",
            "v1.10",
        ]
        versions = [v for v in versions if parse(v) >= parse(minver)]
    return sorted(versions)


def get_stable_version() -> str:
    # read the versions from the git tags
    all_versions = micropython_versions(minver="v1.17")
    return [v for v in all_versions if not v.endswith(V_PREVIEW)][-1]


#############################################################
def wait_for_restart(mcu: MPRemoteBoard, timeout: int = 10):
    """wait for the board to restart"""
    for _ in track(
        range(timeout),
        description="Waiting for the board to restart",
        transient=True,
        get_time=lambda: time.time(),
        show_speed=False,
    ):
        time.sleep(1)
        try:
            mcu.get_mcu_info()
            break
        except ConnectionError:
            pass
