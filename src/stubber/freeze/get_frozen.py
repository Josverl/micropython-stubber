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


import glob

# locating frozen modules :
# tested on MicroPython v1.12 - v1.13
# - 1.16 - using manifests.py, include can specify kwargs
# - 1.13 - using manifests.py, and support for variant
# - 1.12 - using manifests.py, possible also include content of /port/modules folder ?
# - 1.11 and older - include content of /port/modules folder if it exists
import os
from pathlib import Path  # start moving from os & glob to pathlib
from typing import Optional, Union

from loguru import logger as log
from packaging.version import Version
from stubber.utils.config import CONFIG

from .. import utils
from .freeze_folder import freeze_folders  # Micropython < v1.12
from .freeze_manifest_1 import freeze_all_manifests_1 , freeze_one_manifest_1 # Micropython v1.12 - 1.19.1

# globals
FAMILY = "micropython"


def get_frozen(stub_folder: str, version: str, mpy_path: Optional[Union[Path, str]] = None, lib_path: Optional[Union[Path, str]] = None):
    """
    get and parse the to-be-frozen .py modules for micropython to extract the static type information
     - requires that the MicroPython and Micropython-lib repos are checked out and available on a local path
     - repos should be cloned side-by-side as some of the manifests refer to micropython-lib scripts using a relative path
    """

    current_dir = os.getcwd()
    if not mpy_path:
        mpy_path = "./micropython"
    if not lib_path:
        lib_path = "./micropython-lib"
    if not stub_folder:
        stub_folder = "{}/{}_{}_frozen".format(CONFIG.stub_path, FAMILY, utils.clean_version(version, flat=True))
    # get the manifests of the different ports and boards
    mpy_path = Path(mpy_path).absolute().as_posix()
    lib_path = Path(lib_path).absolute().as_posix()
    stub_folder = Path(stub_folder).absolute().as_posix()

    # manifest.py is used for board specific and daily builds
    # manifest_release.py is used for the release builds
    manifests = glob.glob(mpy_path + "/ports/**/manifest.py", recursive=True) + glob.glob(
        mpy_path + "/ports/**/manifest_release.py", recursive=True
    )

    # remove any manifests  that are below one of the virtual environments (venv) \
    # 'C:\\develop\\MyPython\\micropython\\ports\\esp32\\build-venv\\lib64\\python3.6\\site-packages\\pip\\_vendor\\distlib\\manifest.py'
    # and skip the manifest used for coverage tests
    manifests = [m for m in manifests if not "venv" in str(m) and Path(m).parent.name != "coverage"]
    # FIXME check vor version , not count of manifests
    if version in ["latest", "master"] or Version(version) >= Version("1.12"):
        log.debug("MicroPython v1.12 and newer")
        freeze_all_manifests_1(manifests, stub_folder, mpy_path, lib_path, version)
    else:
        log.debug("MicroPython v1.11, older or other")
        # others
        freeze_folders(stub_folder, mpy_path, lib_path, version)
    # restore cwd
    os.chdir(current_dir)
