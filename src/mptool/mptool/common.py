import sys
from pathlib import Path
from typing import Dict, Union

from loguru import logger as log

PORT_FWTYPES = {
    "stm32": ".hex",
    "esp32": ".bin",
    "esp8266": ".bin",
    "rp2": ".uf2",
    "samd": ".uf2",
    "mimxrt": ".hex",
    "nrf": ".hex",
    "renesas-ra": ".hex",
}

DEFAULT_FW_PATH = Path.cwd() / "firmware"
# DEFAULT_FW_PATH = Path.home() / "mp_firmware"

FWInfo = Dict[str, Union[str, bool]]

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
    if version == "latest":
        version = V_PREVIEW
    return version


def set_loglevel(loglevel: str):
    """Set the log level for the logger"""
    try:
        log.remove()
    except ValueError:
        pass
    log.add(sys.stderr, level=loglevel.upper())
