"""Pre/Post Processing for createstubs.py"""
import subprocess
from pathlib import Path
from typing import List

from loguru import logger as log

from .stubmaker import generate_pyi_files

# # log = logging.getLogger(__name__)


def do_post_processing(stub_paths: List[Path], pyi: bool, black: bool):
    "Common post processing"
    for pth in stub_paths:
        if pyi:
            log.debug("Generate type hint files (pyi) in folder: {}".format(pth))
            generate_pyi_files(pth)
        if black:
            run_black(pth)


def run_black(path: Path, capture_output=False):
    """
    run black to format the code / stubs
    """
    cmd = [
        "black",
        path.as_posix(),
    ]
    log.debug("Running black on: {}".format(path))
    # subprocess.run(cmd, capture_output=log.level >= logging.INFO)
    result = subprocess.run(cmd, capture_output=capture_output)
    return result.returncode


def run_autoflake(path: Path, capture_output=False, progress_pyi=False):
    """
    run autoflake to remove unused imports
    needs to be run BEFORE black otherwise it does not recognize long import from`s.
    note: is run file-by-file to include processing .pyi files
    """
    ret = 0
    cmd = [
        "autoflake",
        "-r",
        "--in-place",
        # "--remove-all-unused-imports",
        # "--ignore-init-module-imports",
        path.as_posix(),
        "-v",
        "-v",  # show some feedback
    ]
    log.debug("Running autoflake on: {}".format(path))
    # subprocess.run(cmd, capture_output=log.level >= logging.INFO)
    result = subprocess.run(cmd, capture_output=capture_output)
    if result.returncode != 0:
        log.warning("autoflake failed on: {}".format(file))
        ret = result.returncode

    if progress_pyi:
        for file in list(path.rglob("*.pyi")):

            cmd = [
                "autoflake",
                "-r",
                "--in-place",
                # "--remove-all-unused-imports",
                # "--ignore-init-module-imports",
                file.as_posix(),
                "-v",
                "-v",  # show some feedback
            ]
            log.debug("Running autoflake on: {}".format(path))
            # subprocess.run(cmd, capture_output=log.level >= logging.INFO)
            result = subprocess.run(cmd, capture_output=capture_output)
            if result.returncode != 0:
                log.warning("autoflake failed on: {}".format(file))
                ret = result.returncode

    return ret
