#!/usr/bin/env python3
"""
Collect modules and python stubs from MicroPython source projects (v1.12 +) and stores them in the all_stubs folder
The all_stubs folder should be mapped/symlinked to the micropython_stubs/stubs repo/folder

"""
# pylint: disable= line-too-long,  W1202, invalid-name

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
import glob
import re
import shutil
from typing import Optional
import warnings
import logging
from . import basicgit as git
from . import utils
from .utils.config import CONFIG 

import csv
from collections import defaultdict

from pathlib import Path  # start moving from os & glob to pathlib

# Classes and functions from makemanifest to ensure that the manifest.py files can be processed
from . import makemanifest_2 as makemanifest

import pkgutil
import tempfile

log = logging.getLogger(__name__)
# log.setLevel(level=logging.DEBUG)

# globals
FAMILY = "micropython"


def get_frozen(stub_folder: str, version: str, mpy_folder: Optional[str] = None, lib_folder: Optional[str] = None):
    """
    get and parse the to-be-frozen .py modules for micropython to extract the static type information
     - requires that the MicroPython and Micropython-lib repos are checked out and available on a local path
     - repos should be cloned side-by-side as some of the manifests refer to micropython-lib scripts using a relative path
    """

    current_dir = os.getcwd()
    if not mpy_folder:
        mpy_folder = "./micropython"
    if not lib_folder:
        lib_folder = "./micropython-lib"
    if not stub_folder:
        stub_folder = "{}/{}_{}_frozen".format(CONFIG.stub_path, FAMILY, utils.clean_version(version, flat=True))
    # get the manifests of the different ports and boards
    mpy_folder = Path(mpy_folder).absolute().as_posix()
    lib_folder = Path(lib_folder).absolute().as_posix()
    stub_folder = Path(stub_folder).absolute().as_posix()

    # manifest.py is used for board specific and daily builds
    # manifest_release.py is used for the release builds
    manifests = glob.glob(mpy_folder + "/ports/**/manifest.py", recursive=True) + glob.glob(
        mpy_folder + "/ports/**/manifest_release.py", recursive=True
    )

    # remove any manifests  that are below one of the virtual environments (venv) \
    # 'C:\\develop\\MyPython\\micropython\\ports\\esp32\\build-venv\\lib64\\python3.6\\site-packages\\pip\\_vendor\\distlib\\manifest.py'
    # and skip the manifest used for coverage tests
    manifests = [m for m in manifests if not "venv" in str(m) and Path(m).parent.name != "coverage"]

    if len(manifests) > 0:
        log.info("MicroPython v1.12 and newer")
        get_frozen_from_manifest(manifests, stub_folder, mpy_folder, lib_folder, version)
    else:
        log.info("MicroPython v1.11, older or other")
        # others
        get_frozen_folders(stub_folder, mpy_folder, lib_folder, version)
    # restore cwd
    os.chdir(current_dir)


def get_frozen_folders(stub_folder: str, mpy_folder: str, lib_folder: str, version: str):
    """
    get and parse the to-be-frozen .py modules for micropython to extract the static type information
    locates the to-be-frozen files in modules folders
    - 'ports/<port>/modules/*.py'
    - 'ports/<port>/boards/<board>/modules/*.py'
    """
    match_lib_with_mpy(version_tag=version, lib_folder=lib_folder)

    targets = []
    scripts = glob.glob(mpy_folder + "/ports/**/modules/*.py", recursive=True)
    if len(scripts) > 0:
        # clean target folder
        shutil.rmtree(stub_folder, ignore_errors=True)
    for script in scripts:
        mpy_port, mpy_board = get_target_names(script)
        if not mpy_board:
            mpy_board = "GENERIC"

        dest_path = os.path.join(stub_folder, mpy_port, mpy_board)
        log.info("freeze_internal : {:<30} to {}".format(script, dest_path))
        # ensure folder, including possible path prefix for script
        os.makedirs(dest_path, exist_ok=True)
        # copy file
        try:
            shutil.copy2(script, dest_path)
            if not dest_path in targets:
                targets.append(dest_path)
        except OSError as e:
            ## Ignore errors that are caused by reorganisation of Micropython-lib
            # print(e)
            warnings.warn("unable to freeze {} due to error {}".format(e.filename, str(e)))

    for dest_path in targets:
        # make a module manifest
        port = dest_path.split(os.path.sep)[-2]
        # todo: add board / variant into manifest files ?
        utils.make_manifest(
            Path(dest_path),
            family=FAMILY,
            port=port,
            version=version,
            stubtype="frozen",
        )
    return targets


def get_target_names(path: str) -> tuple:
    "get path to port and board names from a path"
    # https://regexr.com/4sram
    # but with an extra P for Python named groups...
    # regex_port = r"(?P<port>.*[\\/]+ports[\\/]+\w+)[\\/]+boards[\\/]+\w+"              # port
    re_portboard = r".*[\\/]+ports[\\/]+(?P<port>\w+)[\\/]+boards[\\/]+(?P<board>\w+)"  # port & board
    re_port = r".*[\\/]+ports[\\/]+(?P<port>\w+)[\\/]+"  # port
    # matches= re.search(regex, 'C:\\develop\\MyPython\\micropython\\ports\\esp32\\boards\\TINYPICO\\manifest.py')
    # print( matches.group('port'), matches.group('board'))

    mpy_port = mpy_board = None
    matches = re.search(re_portboard, path)
    if matches:
        # port and board
        mpy_port = matches.group("port") or None
        mpy_board = matches.group("board") or None
    else:
        # just port
        matches = re.search(re_port, path)
        if matches:
            mpy_port = matches.group("port") or None
    return mpy_port, mpy_board


def read_micropython_lib_commits(filename="data/micropython_tags.csv"):
    """
    Read a csv with the micropython version and matchin micropython-lib commit-hashes
    these can be used to make sure that the correct micropython-lib version is checked out.

    TODO: it would be nice if micropython-lib had matching commit-tags

    # git for-each-ref --sort=creatordate --format '%(refname) %(creatordate)' refs/tags
    """
    data = pkgutil.get_data(__name__, filename)
    if not data:
        raise Exception(f"Resource {filename} not found")
    version_commit = defaultdict()  # lgtm [py/multiple-definition]
    with tempfile.NamedTemporaryFile(prefix="tags", suffix=".csv", mode="w+t") as ntf:
        ntf.file.write(data.decode(encoding="utf8"))
        ntf.file.seek(0)
        # read the csv file using DictReader
        reader = csv.DictReader(ntf.file, skipinitialspace=True)  # dialect="excel",
        rows = list(reader)
        # create a dict version --> commit_hash
        version_commit = {row["version"].split("/")[-1]: row["lib_commit_hash"] for row in rows if row["version"].startswith("refs/tags/")}
    # add default
    version_commit = defaultdict(lambda: "master", version_commit)
    return version_commit


def match_lib_with_mpy(version_tag: str, lib_folder: str):
    micropython_lib_commits = read_micropython_lib_commits()
    # Make sure that the correct micropython-lib release is checked out
    log.info(f"Matching repo's:  Micropython {version_tag} needs micropython-lib:{micropython_lib_commits[version_tag]}")
    return git.checkout_commit(micropython_lib_commits[version_tag], lib_folder)


def get_frozen_from_manifest(
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

    makemanifest.path_vars["MPY_DIR"] = mpy_folder
    makemanifest.path_vars["MPY_LIB_DIR"] = lib_folder

    # https://regexr.com/4rh39
    # but with an extra P for Python named groups...
    regex_port = r"(?P<port>.*[\\/]+ports[\\/]+\w+)[\\/]+boards[\\/]+\w+"  # port
    regex_port_board = r"(?P<board>(?P<port>.*[\\/]+ports[\\/]+\w+)[\\/]+boards[\\/]+\w+)"  # port & board

    # todo: variants
    # regex_3 = r"(?P<board>(?P<port>.*[\\/]+ports[\\/]+\w+)[\\/]+variants[\\/]+\w+)"  # port & variant

    # matches= re.search(regex, 'C:\\develop\\MyPython\\micropython\\ports\\esp32\\boards\\TINYPICO\\manifest.py')
    # print( matches.group('port'), matches.group('board'))
    match_lib_with_mpy(version_tag=version, lib_folder=lib_folder)

    # Include top-level inputs, to generate the manifest
    for manifest in manifests:
        log.info("Manifest: {}".format(manifest))
        makemanifest.path_vars["PORT_DIR"] = ""
        makemanifest.path_vars["BOARD_DIR"] = ""

        # check BOARD AND PORT pattern
        matches = re.search(regex_port_board, manifest)
        if matches:
            # port and board
            makemanifest.path_vars["PORT_DIR"] = matches.group("port") or ""
            makemanifest.path_vars["BOARD_DIR"] = matches.group("board") or ""
            if os.path.basename(matches.group("board")) == "manifest":
                makemanifest.path_vars["BOARD_DIR"] = ""
        else:
            # TODO: Variants
            matches = re.search(regex_port_board, manifest)  # BOARD AND VARIANT
            if matches:
                # port and variant
                makemanifest.path_vars["PORT_DIR"] = matches.group("port") or ""
                makemanifest.path_vars["BOARD_DIR"] = matches.group("board") or ""
                if os.path.basename(matches.group("board")) == "manifest":
                    makemanifest.path_vars["BOARD_DIR"] = ""
            else:
                # just port
                matches = re.search(regex_port, manifest)
                if matches:
                    makemanifest.path_vars["PORT_DIR"] = matches.group("port") or ""

        port_name = os.path.basename(makemanifest.path_vars["PORT_DIR"])
        board_name = os.path.basename(makemanifest.path_vars["BOARD_DIR"])

        if board_name == "":
            board_name = "GENERIC"

        if board_name == "manifest_release":
            board_name = "RELEASE"

        # set global for later use - must be an absolute path.
        freeze_path = (Path(stub_folder) / port_name / board_name).absolute()

        makemanifest.stub_dir = freeze_path.as_posix()
        # clean target folder
        shutil.rmtree(freeze_path, ignore_errors=True)

        try:
            makemanifest.include(manifest)
        except makemanifest.FreezeError as er:
            log.error('freeze error executing "{}": {}'.format(manifest, er.args[0]))

        # make a module manifest
        utils.make_manifest(Path(makemanifest.stub_dir), FAMILY, port=port_name, board=board_name, version=version, stubtype="frozen")
