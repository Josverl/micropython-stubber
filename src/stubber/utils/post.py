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
    run autoflake to remove unused imports
    needs to be run BEFORE black otherwise it does not recognize long import from`s.
    """
    cmd = [
        "black",
        path.as_posix(),
    ]
    # subprocess.run(cmd, capture_output=log.level >= logging.INFO)
    result = subprocess.run(cmd, capture_output=capture_output)
    return result.returncode


def run_autoflake(path: Path, capture_output=False):
    """
    run autoflake to remove unused imports
    needs to be run BEFORE black otherwise it does not recognize long import from`s.
    """
    cmd = [
        "autoflake",
        "-r",
        "--in-place",
        path.as_posix(),
        "-v",
        "-v",  # show some feedback
    ]
    # subprocess.run(cmd, capture_output=log.level >= logging.INFO)
    result = subprocess.run(cmd, capture_output=capture_output)

    return result.returncode
