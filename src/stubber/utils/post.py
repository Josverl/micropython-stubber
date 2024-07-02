"""Pre/Post Processing for createstubs.py"""

import subprocess
import sys
from pathlib import Path
from typing import List

import autoflake
from mpflash.logger import log

from .stubmaker import generate_pyi_files


def do_post_processing(stub_paths: List[Path], stubgen: bool, black: bool, autoflake: bool):
    "Common post processing"
    for path in stub_paths:
        if stubgen:
            log.debug("Generate type hint files (pyi) in folder: {}".format(path))
            generate_pyi_files(path)
        if black:
            run_black(path)
        if autoflake:
            run_autoflake(path, process_pyi=True)


def run_black(path: Path, capture_output: bool = False):
    """
    run black to format the code / stubs
    """
    log.debug("Running black on: {}".format(path))
    cmd = [
        sys.executable,
        "-m",
        "black",
        path.as_posix(),
        "--line-length",
        "140",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    return result.returncode


def run_autoflake(path: Path, capture_output: bool = False, process_pyi: bool = False):
    """
    run autoflake to remove unused imports
    needs to be run BEFORE black otherwise it does not recognize long import from`s.
    note: is run file-by-file to include processing .pyi files
    """
    if not path.exists():
        log.warning(f"Path does not exist: {path}")
        return -1
    log.info(f"Running autoflake on: {path}")
    # create a list of files to be formatted
    files: List[str] = []
    files.extend([str(f) for f in path.rglob("*.py")])
    if process_pyi:
        files.extend([str(f) for f in path.rglob("*.pyi")])

    # build an argument list
    autoflake_args = {
        "write_to_stdout": False,  # print changed text to stdout
        "in_place": True,  # make changes to files instead of printing diffs
        "remove_all_unused_imports": False,
        "ignore_init_module_imports": False,  # exclude __init__.py when removing unused imports
        "expand_star_imports": False,
        "remove_duplicate_keys": False,
        "remove_unused_variables": False,  # remove all unused imports (not just those from the standard library)
        "remove_rhs_for_unused_variables": False,
        "ignore_pass_statements": False,  # remove pass when superfluous
        "ignore_pass_after_docstring": False,  # ignore pass statements after a newline ending on '"""'
        "check": False,  # return error code if changes are needed
        "check_diff": False,
        "quiet": False,
    }
    # format the files
    exit_status = 0
    for name in files:
        log.debug(f"Running autoflake on: {name}")
        exit_status |= autoflake.fix_file(name, args=autoflake_args)
