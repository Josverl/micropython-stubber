"""
Freeze manifest files for micropython 1.16 and later
uses the manifestfile.py to generate frozen stubs

"""

import os
import shutil
from pathlib import Path
from typing import List, Optional

from mpflash.logger import log

from stubber import utils
from stubber.tools.manifestfile import (
    MODE_FREEZE,
    ManifestFile,
    ManifestFileError,
    ManifestOutput,
)
from stubber.utils.config import CONFIG

from .common import apply_frozen_module_fixes, get_freeze_path, get_portboard


def make_path_vars(
    *,
    mpy_path: Path = CONFIG.mpy_path,
    mpy_lib_path: Path = CONFIG.mpy_lib_path,  # ? if <= 1.19.1
    port: Optional[str] = None,
    board: Optional[str] = None,
):
    if port is None or port == "":  # pragma: no cover
        port_path = mpy_path
    else:
        port_path = mpy_path / "ports" / port

    if board is None or board == "":  # pragma: no cover
        board_path = port_path
    else:
        board_path = port_path / "boards" / board

    log.trace(f"port_path : {port_path}")
    log.trace(f"board_path: {board_path}")
    if not port_path.exists():  # pragma: no cover
        raise ValueError("port board path not found")
    if not board_path.exists():  # pragma: no cover
        raise ValueError("board path not found")

    # VARS must be absolute paths
    vars = {
        "MPY_DIR": mpy_path.absolute().as_posix(),
        "MPY_LIB_DIR": mpy_lib_path.absolute().as_posix(),
        "PORT_DIR": port_path.absolute().as_posix(),
        "BOARD_DIR": board_path.absolute().as_posix(),
    }

    if board and "ARDUINO" in board:
        log.warning(f"HACK- Adding [TOP]/lib/arduino-lib to paths: {board}")
        # see micropython/ports/renesas-ra/boards/ARDUINO_PORTENTA_C33/mpconfigboard.mk
        vars["ARDUINO_LIB_DIR"] = (mpy_path / "lib/arduino-lib").absolute().as_posix()

    if port == "alif":
        # alif port uses MCU_CORE ?= M55_HP - see micropython/ports/alif/boards/manifest.py
        log.warning(f"alif - Adding MCU_CORE='HP' to vars")
        vars["MCU_CORE"] = "HP"
    elif port == "zephyr":
        # make sure the port/zephyr/modules folder exists
        (mpy_path / "ports/zephyr/modules").mkdir(parents=True, exist_ok=True)

    return vars


def freeze_one_manifest_2(
    manifest: Path,
    frozen_stub_path: Path,
    mpy_path: Path,
    mpy_lib_path: Path,
    version: str,
):
    # apparently there can be multiple manifest files to a board ?
    # save cwd for 'misbehaving' older esp8266 manifest files
    cwd = Path.cwd()
    # so we need to get the port and board from the path
    log.debug(f"input_manifest: {manifest}")
    port, board = get_portboard(manifest)

    log.info("port-board: {}".format((port + "-" + board).rstrip("-")))

    path_vars = make_path_vars(port=port, board=board, mpy_path=mpy_path, mpy_lib_path=mpy_lib_path)
    upy_manifest = ManifestFile(MODE_FREEZE, path_vars)
    try:
        # manifest needs to be run from the port's folder
        os.chdir(path_vars["PORT_DIR"])
        upy_manifest.execute(manifest.as_posix())
    except ManifestFileError as er:
        log.error('freeze error executing "{}": {}'.format(manifest, er.args[0]))
        raise er
    log.debug(f"total {len(upy_manifest.files())} files")

    # restore working directory
    os.chdir(cwd)
    # save the frozen files to the stubs
    copy_frozen_to_stubs(frozen_stub_path, port, board, upy_manifest.files(), version, mpy_path=mpy_path)


def copy_frozen_to_stubs(
    stub_path: Path,
    port: str,
    board: str,
    files: List[ManifestOutput],
    version: str,
    mpy_path: Path,
):
    """
    copy the frozen files from the manifest to the stubs folder

    stubpath = the destination : # stubs/{family}-{version}-frozen
    """
    freeze_path, board = get_freeze_path(stub_path, port, board)

    log.debug(f"copy frozen: {port}-{board} to {freeze_path}")
    freeze_path.mkdir(parents=True, exist_ok=True)
    # clean target folder
    shutil.rmtree(freeze_path, ignore_errors=True)

    # print(tabulate(files))
    # copy the frozen files to the stubs
    for f in files:
        dest = freeze_path / f.target_path
        log.trace(f"copying {f.full_path} to {f.target_path}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy(f.full_path, dest)
        except OSError as er:
            log.warning(f"error copying {f.full_path} to {dest}: {er}")
            raise er
            # try to continue

    apply_frozen_module_fixes(freeze_path, mpy_path=mpy_path)

    # make a module manifest
    FAMILY = "micropython"
    utils.make_manifest(freeze_path, FAMILY, port=port, board=board, version=version, stubtype="frozen")
