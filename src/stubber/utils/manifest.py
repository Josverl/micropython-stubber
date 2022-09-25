import json
import os
from pathlib import Path
from typing import Optional

from .my_version import __version__
from .versions import clean_version

# # log = logging.getLogger(__name__)
# # logging.basicConfig(level=logging.INFO)


def manifest(
    family: str = "micropython",
    stubtype: str = "frozen",
    machine: Optional[str] = None,  # also frozen.variant
    port: Optional[str] = None,
    platform: Optional[str] = None,
    sysname: Optional[str] = None,
    nodename: Optional[str] = None,
    version: Optional[str] = None,
    release: Optional[str] = None,
    firmware: Optional[str] = None,
) -> dict:
    "create a new empty manifest dict"

    machine = machine or family  # family
    port = port or "common"  # family
    platform = platform or port  # family
    version = version or "0.0.0"
    sysname = sysname or ""
    nodename = nodename or sysname or ""
    release = release or version or ""
    if firmware is None:
        firmware = "{}-{}-{}".format(family, port, clean_version(version, flat=True))
        # remove double dashes x2
        firmware = firmware.replace("--", "-")
        firmware = firmware.replace("--", "-")

    mod_manifest = {
        "$schema": "https://raw.githubusercontent.com/Josverl/micropython-stubber/main/data/schema/stubber-v1_4_0.json",
        "firmware": {
            "family": family,
            "port": port,
            "platform": platform,
            "machine": machine,
            "firmware": firmware,
            "nodename": nodename,
            "version": version,
            "release": release,
            "sysname": sysname,
        },
        "stubber": {
            "version": __version__,
            "stubtype": stubtype,
        },
        "modules": [],
    }
    return mod_manifest


def make_manifest(folder: Path, family: str, port: str, version: str, release: str = "", stubtype: str = "", board: str = "") -> bool:
    """Create a `module.json` manifest listing all files/stubs in this folder and subfolders."""
    mod_manifest = manifest(family=family, port=port, machine=board, sysname=family, version=version, release=release, stubtype=stubtype)
    try:
        # list all *.py files, not strictly modules but decent enough for documentation
        files = list(folder.glob("**/*.py"))
        if len(files) == 0:
            files = list(folder.glob("**/*.pyi"))

        # sort the list
        for file in sorted(files):
            # if file is in folder, then use relative path only
            # use old style relative path determination to support # python 3.8
            file = Path(os.path.relpath(file, start=folder))
            # if file.is_relative_to(folder):
            #     file = file.relative_to(folder)

            mod_manifest["modules"].append(
                {
                    "file": file.as_posix(),
                    "module": file.stem,
                }
            )

        # write the the module manifest
        with open(folder / "modules.json", "w") as outfile:
            json.dump(mod_manifest, outfile, indent=4)
        return True
    except OSError:
        return False
