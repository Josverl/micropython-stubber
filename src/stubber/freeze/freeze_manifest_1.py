#!/usr/bin/env python3
"""
Collect modules and python stubs from MicroPython source projects (v1.12 +) and stores them in the all_stubs folder
The all_stubs folder should be mapped/symlinked to the micropython_stubs/stubs repo/folder

"""

# Copyright (c) 2022 Jos Verlinde
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
import re
import shutil
from pathlib import Path  # start moving from os & glob to pathlib

from loguru import logger as log
from stubber.freeze.common import apply_frozen_module_fixes, get_freeze_path, get_portboard
from stubber.freeze.freeze_manifest_2 import make_path_vars
from stubber.utils.config import CONFIG
from stubber.utils.repos import match_lib_with_mpy

from .. import utils

# Classes and functions from makemanifest to ensure that the manifest.py files can be processed
from . import makemanifest_1 as makemanifest

# globals
FAMILY = "micropython"

# https://regexr.com/4rh39
# but with an extra P for Python named groups...
regex_port = r"(?P<port>.*[\\/]+ports[\\/]+\w+)[\\/]+boards[\\/]+\w+"  # port
regex_port_board = r"(?P<board>(?P<port>.*[\\/]+ports[\\/]+\w+)[\\/]+boards[\\/]+\w+)"  # port & board


def freeze_all_manifests_1(
    manifests,
    stub_folder: str,
    mpy_folder: str,
    lib_folder: str,
    version: str,
):
    """
    get and parse the to-be-frozen .py modules for micropython to extract the static type information
    locates the to-be-frozen files through the manifest.py introduced in MicroPython 1.12
    - manifest.py is used for board specific and daily builds
    - manifest_release.py is used for the release builds
    """

    stub_folder = os.path.abspath(stub_folder)

    match_lib_with_mpy(version_tag=version, lib_folder=lib_folder)

    # Include top-level inputs, to generate the manifest
    for manifest in manifests:
        log.debug("Manifest: {}".format(manifest))

        freeze_one_manifest_1(manifest, stub_folder, mpy_folder, lib_folder, version)


def freeze_one_manifest_1(
    manifest: str,
    stub_folder: str,
    mpy_folder: str,
    mpy_lib_folder: str,
    version,
):
    """
    get and parse the to-be-frozen .py modules for micropython to extract the static type information
    locates the to-be-frozen files through the manifest.py introduced in MicroPython 1.12
    Suitable for version v1.12 -  v1.19
    - manifest.py is used for board specific and daily builds
    - manifest_release.py is used for the release builds
    """
    mpy_path = Path(mpy_folder)
    mpy_lib_path = Path(mpy_lib_folder)

    port, board = get_portboard(Path(manifest))
    path_vars = make_path_vars(port=port, board=board, mpy_path=mpy_path, mpy_lib_path=Path(mpy_lib_folder))

    # NOTE: perhaps copy all path vars ?
    makemanifest.path_vars = path_vars
    # makemanifest.path_vars["PORT_DIR"] = path_vars["PORT_DIR"]
    # makemanifest.path_vars["BOARD_DIR"] = path_vars["BOARD_DIR"]
    # makemanifest.path_vars["MPY_DIR"] = mpy_folder
    # makemanifest.path_vars["MPY_LIB_DIR"] = mpy_lib_folder

    # set global for later use - must be an absolute path.
    freeze_path, board = get_freeze_path(Path(stub_folder), port, board)

    makemanifest.stub_dir = freeze_path.as_posix()
    # clean target folder
    shutil.rmtree(freeze_path, ignore_errors=True)

    try:
        makemanifest.include(manifest)
    except (makemanifest.FreezeError, NameError) as er:
        log.error('freeze error executing "{}": {}'.format(manifest, er.args[0]))

    apply_frozen_module_fixes(freeze_path, mpy_path=mpy_path)

    # make a module manifest
    utils.make_manifest(Path(makemanifest.stub_dir), FAMILY, port=port, board=board, version=version, stubtype="frozen")
