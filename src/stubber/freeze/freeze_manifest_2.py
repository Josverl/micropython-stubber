import os
import shutil
from pathlib import Path
from typing import List, Optional

import stubber.basicgit as git
import stubber.tools.manifestfile as manifestfile
from loguru import logger as log
from stubber import utils
from stubber.tools.manifestfile import ManifestOutput
from stubber.utils.config import CONFIG

from .common import apply_frozen_module_fixes, get_freeze_path, get_portboard

def make_path_vars(
    *,
    mpy_path: Path = CONFIG.mpy_path,
    mpy_lib_path: Path = CONFIG.mpy_lib_path,  # ? if <= 1.19.1
    port: Optional[str] = None,
    board: Optional[str] = None,
):
    if port == None or port == "": # pragma: no cover
        port_path = mpy_path
    else:
        port_path = mpy_path / "ports" / port

    if board == None or board == "": # pragma: no cover
        board_path = port_path
    else:
        board_path = port_path / "boards" / board

    log.trace(f"port_path : {port_path}")
    log.trace(f"board_path: {board_path}")
    if not port_path.exists(): # pragma: no cover
        raise ValueError("port board path not found")
    if not board_path.exists(): # pragma: no cover
        raise ValueError("board path not found")

    # VARS must be absolute paths
    path_vars = {
        "MPY_DIR": mpy_path.absolute().as_posix(),
        "MPY_LIB_DIR": mpy_lib_path.absolute().as_posix(),
        "PORT_DIR": port_path.absolute().as_posix(),
        "BOARD_DIR": board_path.absolute().as_posix(),
    }
    return path_vars


def get_frozen_from_manifest_2(frozen_stub_path: Path, mpy_path: Path, mpy_lib_path: Path, version):
    """
    process all the manifests under the ports folder and update the frozen filesin the stubs folder
    """
    # we are goning to jump around, avoid relative paths
    frozen_stub_path = frozen_stub_path.absolute()
    mpy_path = mpy_path.absolute()
    mpy_lib_path = mpy_lib_path.absolute()

    manifests = [
        m.absolute()
        for m in (CONFIG.mpy_path / "ports").glob("**/manifest.py")
        if Path(m).parent.name != "coverage" and not "venv" in m.parts
    ]

    if len(manifests) > 0:
        log.info(f"manifests: {len(manifests)}")
        shutil.rmtree(frozen_stub_path, ignore_errors=True)

    for input_manifest in manifests:
        # apparently there can be multiple manifest files to a board ?
        # save cwd for 'misbehaving' older esp8266 manifest files
        cwd = Path.cwd()
        # so we need to get the port and board from the path
        log.info(f"input_manifest: {input_manifest}")
        port, board = get_portboard(input_manifest)
        log.info(f"port-board: '{port}-{board}'")

        path_vars = make_path_vars(port=port, board=board, mpy_path=mpy_path, mpy_lib_path=mpy_lib_path)
        manifest = manifestfile.ManifestFile(manifestfile.MODE_FREEZE, path_vars)
        try:
            # assume manifestneeds to be run from the port's folder
            os.chdir(path_vars["PORT_DIR"])
            manifest.execute(input_manifest.as_posix())
        except manifestfile.ManifestFileError as er:
            log.error('freeze error executing "{}": {}'.format(input_manifest, er.args[0]))
            continue
        log.info(f"total {len(manifest.files())} files")

        # restore working directory
        os.chdir(cwd)

        # save the frozen files to the stubs
        copy_frozen_to_stubs(frozen_stub_path, port, board, manifest.files(), version, mpy_path=mpy_path)


def copy_frozen_to_stubs(stub_path: Path, port: str, board: str, files: List[ManifestOutput], version, mpy_path: Path):
    """
    copy the frozen files from the manifest to the stubs folder

    stubpath = the destination : # stubs/{family}-{version}-frozen
    """
    freeze_path, board = get_freeze_path(stub_path, port, board)
    # if board == "":
    #     board = "GENERIC"

    # if board == "manifest_release":
    #     board = "RELEASE"
    # # set global for later use - must be an absolute path.
    # freeze_path = (stub_path / port / board).resolve()

    log.info(f"copy frozen: {port}-{board} to {freeze_path}")
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
            # try to continue

    apply_frozen_module_fixes(freeze_path, mpy_path=mpy_path)

    # make a module manifest
    FAMILY = "micropython"
    utils.make_manifest(freeze_path, FAMILY, port=port, board=board, version=version, stubtype="frozen")


if __name__ == "__main__":
    version = utils.clean_version(git.get_tag(CONFIG.mpy_path.as_posix()) or "0.0")
    family = "micropython"
    stub_path = CONFIG.stub_path / f"{family}-{utils.clean_version(version, flat=True)}-frozen"

    if version == "latest":  # >= 1.19.1
        # after 1.19.1 micopython-lib is a submodule of micropython
        lib_path = CONFIG.mpy_path / "lib/micropython-lib"
    else:
        lib_path = CONFIG.mpy_lib_path

    get_frozen_from_manifest_2(
        frozen_stub_path=stub_path,
        mpy_path=CONFIG.mpy_path,
        mpy_lib_path=lib_path,
        version=version,
    )
    stub_paths: List[Path] = [stub_path]
    utils.do_post_processing(stub_paths, pyi=True, black=True)
