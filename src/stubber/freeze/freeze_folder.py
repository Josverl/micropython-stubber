import glob
import os
import shutil
import warnings
from pathlib import Path  # start moving from os & glob to pathlib

from loguru import logger as log
from stubber.utils.repos import match_lib_with_mpy

from .. import utils

# Classes and functions from makemanifest to ensure that the manifest.py files can be processed
from .common import get_freeze_path, get_portboard

# globals
FAMILY = "micropython"


def freeze_folders(stub_folder: str, mpy_folder: str, lib_folder: str, version: str):
    """
    get and parse the to-be-frozen .py modules for micropython to extract the static type information
    locates the to-be-frozen files in modules folders
    - 'ports/<port>/modules/*.py'
    - 'ports/<port>/boards/<board>/modules/*.py'
    """
    match_lib_with_mpy(version_tag=version, lib_path=Path(lib_folder))

    targets = []
    scripts = glob.glob(mpy_folder + "/ports/**/modules/*.py", recursive=True)
    if len(scripts) > 0:
        # clean target folder
        shutil.rmtree(stub_folder, ignore_errors=True)
    for script in scripts:
        port, board = get_portboard(Path(script))

        freeze_path, board = get_freeze_path(Path(stub_folder), port, board)
        dest_path = freeze_path.as_posix()
        # if board == "":
        #     board = "GENERIC"

        # dest_path = os.path.join(stub_folder, port, board)

        log.debug("freeze_internal : {:<30} to {}".format(script, dest_path))
        # ensure folder, including possible path prefix for script
        os.makedirs(dest_path, exist_ok=True)
        # copy file
        try:
            shutil.copy2(script, dest_path)
            if not dest_path in targets:
                targets.append(dest_path)
        except OSError as e:
            ## Ignore errors that are caused by reorganisation of Micropython-lib
            # log.exception(e)
            warnings.warn("unable to freeze {} due to error {}".format(e.filename, str(e)))

    for dest_path in targets:
        # make a module manifest
        port = dest_path.split("/")[-2]
        # todo: add board / variant into manifest files ?
        utils.make_manifest(
            Path(dest_path),
            family=FAMILY,
            port=port,
            version=version,
            stubtype="frozen",
        )
    return targets
