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
import warnings
import logging
import basicgit as git
import utils
from pathlib import Path  # start moving from os & glob to pathlib


log = logging.getLogger(__name__)
# log.setLevel(level=logging.DEBUG)

# globals
FAMILY = "micropython"

path_vars = {"MPY_DIR": "", "MPY_LIB_DIR": "", "PORT_DIR": "", "BOARD_DIR": ""}
stub_dir = None

# Classes and functions from makemanifest to ensure that the manifest.py files can be processed
# do not change class name
class FreezeError(Exception):
    pass


# do not change class name
class IncludeOptions:
    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self._defaults = {}

    def defaults(self, **kwargs):
        self._defaults = kwargs

    def __getattr__(self, name):
        return self._kwargs.get(name, self._defaults.get(name, None))


# do not change method name
# freeze_as_mpy is only used by the unix port.
def freeze_as_mpy(path, script=None, opt=0):
    log.debug(" - freeze_as_mpy({},script={},opt={})".format(path, script, opt))
    freeze(path, script, opt)


# do not change method name
def freeze_as_str(path):
    log.debug(" - freeze_as_str({})".format(path))
    freeze(path)


# do not change method name
def freeze_mpy(path, script=None, opt=0):
    """Freeze the input (see above), which must be .mpy files that are
    frozen directly.
    """
    log.debug(" - freeze_as_mpy({})".format(path))
    freeze(path, script)


# function used commonly in manifest.py to freeze a set of scripts
# pylint: disable=unused-argument, unused-variable
# do not change method name
def freeze(path, script=None, opt=0):
    """Freeze the input, automatically determining its type.  A .py script
    will be compiled to a .mpy first then frozen, and a .mpy file will be
    frozen directly.

    `path` must be a directory, which is the base directory to search for
    files from.  When importing the resulting frozen modules, the name of
    the module will start after `path`, ie `path` is excluded from the
    module name.

    If `path` is relative, it is resolved to the current manifest.py.
    Use $(MPY_DIR), $(MPY_LIB_DIR), $(PORT_DIR), $(BOARD_DIR) if you need
    to access specific paths.

    If `script` is None all files in `path` will be frozen.

    If `script` is an iterable then freeze() is called on all items of the
    iterable (with the same `path` and `opt` passed through).

    If `script` is a string then it specifies the filename to freeze, and
    can include extra directories before the file.  The file will be
    searched for in `path`.

    `opt` is the optimisation level to pass to mpy-cross when compiling .py
    to .mpy. (ignored in this implementation)
    """
    log.debug(" - freeze(({},script={},opt={})".format(path, script, opt))
    path = convert_path(path)
    if script is None:
        # folder of scripts.
        # for s in os.listdir(path):
        #     freeze_internal(path, s)

        for dirpath, dirnames, filenames in os.walk(path, followlinks=True):
            for script in filenames:
                # can recurse folder, so add relative path to script.
                freeze_internal(path, (dirpath + "/" + script)[len(path) + 1 :])
                # freeze_internal(kind, path, (dirpath + '/' + f)[len(path) + 1:], opt)
    elif not isinstance(script, str):
        # several specific scripts.
        for script in script:
            freeze_internal(path, script)
    else:
        # on specific script, may include a path: 'umqtt/simple.py'
        freeze_internal(path, script)


# called by freeze.
# do not change method name
def freeze_internal(path: str, script: str):
    """
    Copy the to-be-frozen module to the destination folder to be stubbed.

    Parameters:
    path (str)  : the destination
    script (str): the source script to be frozen
    """

    log.debug(" - freeze_internal({},{})".format(path, script))
    path = convert_path(path)
    if not os.path.isdir(path):
        raise FreezeError("freeze path must be a directory")

    script_path = os.path.join(path, script)

    if stub_dir:
        log.info("freeze_internal : {:<30} to {}".format(script, stub_dir))
        dest_path = os.path.dirname(os.path.join(stub_dir, script))
        # ensure folder, including possible path prefix for script
        os.makedirs(dest_path, exist_ok=True)
        # copy file
        try:
            shutil.copy2(script_path, dest_path)
        except (FileNotFoundError) as e:
            log.warning(f"File {path}/{script} not found")
        except (OSError, FileNotFoundError) as e:
            log.exception(e)
    else:
        raise FreezeError("Stub folder not set")


# do not change method name
def include(manifest, **kwargs):
    """
    Include another manifest.

    The manifest argument can be a string (filename) or an iterable of
    strings.

    Relative paths are resolved with respect to the current manifest file.

    Optional kwargs can be provided which will be available to the
    included script via the `options` variable.

    e.g. include("path.py", extra_features=True)

    in path.py:
        options.defaults(standard_features=True)

        # freeze minimal modules.
        if options.standard_features:
            # freeze standard modules.
        if options.extra_features:
            # freeze extra modules.
    """
    if not isinstance(manifest, str):
        for m in manifest:
            include(m)
    else:
        manifest = convert_path(manifest)
        with open(manifest) as f:
            # Make paths relative to this manifest file while processing it.
            # Applies to includes and input files.
            prev_cwd = os.getcwd()
            os.chdir(os.path.dirname(manifest))
            try:
                # exec(f.read())  # pylint: disable=exec-used
                exec(f.read(), globals(), {"options": IncludeOptions(**kwargs)})  # pylint: disable=exec-used
            except OSError:
                log.warning("Could not process manifest: {}".format(manifest))
            os.chdir(prev_cwd)


def convert_path(path):
    "Perform variable substitution in path"
    for name, value in path_vars.items():
        path = path.replace("$({})".format(name), value)
    # Convert to absolute path (so that future operations don't rely on
    # still being chdir 'ed).
    return os.path.abspath(path)


def get_frozen(stub_path: str, version: str, mpy_path: str = None, lib_path: str = None):
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
    if not stub_path:
        stub_path = "{}/{}_{}_frozen".format(utils.STUB_FOLDER, FAMILY, utils.flat_version(version))
    # get the manifests of the different ports and boards
    mpy_path = os.path.abspath(mpy_path)
    lib_path = os.path.abspath(lib_path)
    stub_path = os.path.abspath(stub_path)

    # manifest.py is used for board specific and daily builds
    # manifest_release.py is used for the release builds
    manifests = glob.glob(mpy_path + "/ports/**/manifest.py", recursive=True) + glob.glob(
        mpy_path + "/ports/**/manifest_release.py", recursive=True
    )

    # remove any manifests  that are below one of the virtual environments (venv) \
    # 'C:\\develop\\MyPython\\micropython\\ports\\esp32\\build-venv\\lib64\\python3.6\\site-packages\\pip\\_vendor\\distlib\\manifest.py'
    manifests = [m for m in manifests if not "venv" in m]

    if len(manifests) > 0:
        log.debug("MicroPython v1.12 and newer")
        get_frozen_manifest(manifests, stub_path, mpy_path, lib_path, version)
    else:
        log.debug("MicroPython v1.11, older or other")
        # others
        get_frozen_folders(stub_path, mpy_path, lib_path, version)
    # restore cwd
    os.chdir(current_dir)


def get_frozen_folders(stub_path: str, mpy_path: str, lib_path: str, version: str):
    """
    get and parse the to-be-frozen .py modules for micropython to extract the static type information
    locates the to-be-frozen files in modules folders
    - 'ports/<port>/modules/*.py'
    - 'ports/<port>/boards/<board>/modules/*.py'
    """
    targets = []
    scripts = glob.glob(mpy_path + "/ports/**/modules/*.py", recursive=True)
    for script in scripts:
        mpy_port, mpy_board = get_target_names(script)
        if not mpy_board:
            mpy_board = "GENERIC"

        dest_path = os.path.join(stub_path, mpy_port, mpy_board)
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


def get_frozen_manifest(
    manifests,
    stub_path: str,
    mpy_path: str,
    lib_path: str,
    version: str,
):
    """
    get and parse the to-be-frozen .py modules for micropython to extract the static type information
    locates the to-be-frozen files through the manifest.py introduced in MicroPython 1.12
    - manifest.py is used for board specific and daily builds
    - manifest_release.py is used for the release builds
    """

    global path_vars  # pylint: disable=global-statement
    global stub_dir  # pylint: disable=global-statement

    stub_path = os.path.abspath(stub_path)

    path_vars["MPY_DIR"] = mpy_path
    path_vars["MPY_LIB_DIR"] = lib_path

    # https://regexr.com/4rh39
    # but with an extra P for Python named groups...
    regex_port = r"(?P<port>.*[\\/]+ports[\\/]+\w+)[\\/]+boards[\\/]+\w+"  # port
    regex_port_board = r"(?P<board>(?P<port>.*[\\/]+ports[\\/]+\w+)[\\/]+boards[\\/]+\w+)"  # port & board

    # todo: variants
    # regex_3 = r"(?P<board>(?P<port>.*[\\/]+ports[\\/]+\w+)[\\/]+variants[\\/]+\w+)"  # port & variant

    # matches= re.search(regex, 'C:\\develop\\MyPython\\micropython\\ports\\esp32\\boards\\TINYPICO\\manifest.py')
    # print( matches.group('port'), matches.group('board'))

    # Include top-level inputs, to generate the manifest
    for manifest in manifests:
        log.info("Manifest: {}".format(manifest))
        path_vars["PORT_DIR"] = ""
        path_vars["BOARD_DIR"] = ""

        # check BOARD AND PORT pattern
        matches = re.search(regex_port_board, manifest)  
        if matches:
            # port and board
            path_vars["PORT_DIR"] = matches.group("port") or ""
            path_vars["BOARD_DIR"] = matches.group("board") or ""
            if os.path.basename(matches.group("board")) == "manifest":
                path_vars["BOARD_DIR"] = ""
        else:
            # TODO: Variants
            matches = re.search(regex_port_board, manifest)  # BOARD AND VARIANT
            if matches:
                # port and variant
                path_vars["PORT_DIR"] = matches.group("port") or ""
                path_vars["BOARD_DIR"] = matches.group("board") or ""
                if os.path.basename(matches.group("board")) == "manifest":
                    path_vars["BOARD_DIR"] = ""
            else:
                # just port
                matches = re.search(regex_port, manifest)
                if matches:
                    path_vars["PORT_DIR"] = matches.group("port") or ""

        port_name = os.path.basename(path_vars["PORT_DIR"])
        board_name = os.path.basename(path_vars["BOARD_DIR"])

        if board_name == "":
            board_name = "GENERIC"

        if board_name == "manifest_release":
            board_name = "RELEASE"

        # set global for later use - must be an absolute path.
        stub_dir = os.path.abspath(os.path.join(stub_path, port_name, board_name))

        try:
            include(manifest)
        except FreezeError as er:
            log.error('freeze error executing "{}": {}'.format(manifest, er.args[0]))

        # make a module manifest
        utils.make_manifest(Path(stub_dir), FAMILY, port=port_name, board=board_name, version=version, stubtype="frozen")


if __name__ == "__main__":
    "just gather for the current version"
    logging.basicConfig(format="%(levelname)-8s:%(message)s", level=logging.INFO)
    mpy_path = "./micropython"
    lib_path = "./micropython-lib"
    version = utils.clean_version(git.get_tag(mpy_path) or "0.0")

    if version:
        log.info("found micropython version : {}".format(version))
        # folder/{family}_{version}_frozen
        stub_path = utils.stubfolder("{}-{}-frozen".format(FAMILY, utils.flat_version(version)))
        get_frozen(stub_path, version=version, mpy_path=mpy_path, lib_path=lib_path)
        exit(0)
    else:
        log.warning("Unable to find the micropython repo in folder : {}".format(mpy_path))
        exit(1)
