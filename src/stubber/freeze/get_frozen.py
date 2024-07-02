#!/usr/bin/env python3
"""
Collect modules and python stubs from MicroPython source projects (v1.12 +) and stores them in the all_stubs folder
The all_stubs folder should be mapped/symlinked to the micropython_stubs/stubs repo/folder

"""

# Copyright (c) 2020 Jos Verlinde
# MIT license
# some functions used from micropython/micropython/tools/makemanifest.py,
#   part of the MicroPython project, http://micropython.org/
#   Copyright (c) 2019 Damien P. George

# locating frozen modules :
# tested on MicroPython v1.12 - v1.13
# - 1.16 - using manifests.py, include can specify kwargs
# - 1.13 - using manifests.py, and support for variant
# - 1.12 - using manifests.py, possible also include content of /port/modules folder ?
# - 1.11 and older - include content of /port/modules folder if it exists
import os
import shutil  # start moving from os & glob to pathlib
from pathlib import Path
from typing import List, Optional

from mpflash.logger import log
from packaging.version import Version

from mpflash.versions import SET_PREVIEW, V_PREVIEW
from stubber import utils
from stubber.freeze.freeze_folder import freeze_folders  # Micropython < v1.12
from stubber.freeze.freeze_manifest_2 import freeze_one_manifest_2
from stubber.utils.config import CONFIG

FAMILY = "micropython"


def get_manifests(mpy_path: Path) -> List[Path]:
    """
    Returns a list of all manifests.py files found in the ports folder of the MicroPython repo
    """
    log.info(f"looking for manifests in  {mpy_path}")
    all_manifests = [
        m.absolute()
        for m in (mpy_path / "ports").rglob("manifest.py")
        if Path(m).parent.name != "coverage" and "venv" not in m.parts and ".venv" not in m.parts
    ]
    log.info(f"manifests found: {len(all_manifests)}")
    return all_manifests


def add_comment_to_path(path: Path, comment: str) -> None:
    """
    Add a comment to the top of each file in the path
    using a codemod
    """
    # TODO: #305 add comment line to each file with the micropython version it was generated from
    # frozen_stub_path
    # python -m libcst.tool codemod --include-stubs --no-format  add_comment.AddComment .\repos\micropython-stubs\stubs\micropython-v1_19_1-frozen\ --comment "# Micropython 1.19.1 frozen stubs"
    pass


def freeze_any(
    stub_folder: Optional[Path] = None,
    version: str = V_PREVIEW,
    mpy_path: Optional[Path] = None,
    mpy_lib_path: Optional[Path] = None,
) -> Path:
    """
    Get and parse the to-be-frozen .py modules for micropython to extract the static type information
     - requires that the MicroPython and Micropython-lib repos are checked out and available on a local path
     - repos should be cloned side-by-side as some of the manifests refer to micropython-lib scripts using a relative path

    The micropython-* repos must be checked out to the required version/tag.

    """
    count = 0
    current_dir = os.getcwd()
    mpy_path = Path(mpy_path).absolute() if mpy_path else CONFIG.mpy_path.absolute()
    mpy_lib_path = Path(mpy_lib_path).absolute() if mpy_lib_path else CONFIG.mpy_path.absolute()

    # if old version of micropython, use the old freeze method
    if version not in SET_PREVIEW and Version(version) <= Version("1.11"):
        frozen_stub_path = get_fsp(version, stub_folder)
        log.debug("MicroPython v1.11, older or other")
        # others
        modules = freeze_folders(
            frozen_stub_path.as_posix(), mpy_path.as_posix(), mpy_lib_path.as_posix(), version
        )
        count = len(modules)
    else:
        # get the current checked out version
        version = utils.checkedout_version(CONFIG.mpy_path)

        frozen_stub_path = get_fsp(version, stub_folder)
        # get the manifests of the different ports and boards
        all_manifests = get_manifests(mpy_path)

        # process all_manifests under the ports folder and update the frozen files in the stubs folder
        # we are going to jump around, avoid relative paths
        mpy_path = mpy_path.absolute()
        mpy_lib_path = mpy_lib_path.absolute()

        if len(all_manifests) > 0:
            log.info(f"manifests: {len(all_manifests)}")
            shutil.rmtree(frozen_stub_path, ignore_errors=True)
        else:
            log.warning("no manifests found")
        for manifest in all_manifests:
            try:
                freeze_one_manifest_2(manifest, frozen_stub_path, mpy_path, mpy_lib_path, version)
                count += 1
            except Exception as e:
                log.error(f"Error processing manifest {manifest} : {e}")

    # add comment line to each file with the micropython version it was generated from
    add_comment_to_path(frozen_stub_path, f"# Micropython {version} frozen stubs")

    # restore cwd
    os.chdir(current_dir)
    return frozen_stub_path


def get_fsp(version: str, stub_folder: Optional[Path] = None) -> Path:
    if not stub_folder:
        frozen_stub_path = (
            CONFIG.stub_path / f"{FAMILY}-{utils.clean_version(version, flat=True)}-frozen"
        )
        frozen_stub_path = frozen_stub_path.absolute()
    else:
        frozen_stub_path: Path = Path(stub_folder).absolute()
    return frozen_stub_path
