"""Pre/Post Processing for createstubs.py"""
import subprocess
from pathlib import Path
from typing import List

import autoflake
from loguru import logger as log

from .stubmaker import generate_pyi_files

# # log = logging.getLogger(__name__)


def do_post_processing(stub_paths: List[Path], pyi: bool, black: bool):
    "Common post processing"
    for path in stub_paths:
        if pyi:
            log.debug("Generate type hint files (pyi) in folder: {}".format(path))
            generate_pyi_files(path)
        if black:
            run_black(path)


def run_black(path: Path, capture_output: bool = False):
    """
    run black to format the code / stubs
    """
    cmd = [
        "black",
        path.as_posix(),
        "--line-length",
        "140",
    ]
    log.debug("Running black on: {}".format(path))
    # subprocess.run(cmd, capture_output=log.level >= logging.INFO)
    result = subprocess.run(cmd, capture_output=capture_output)
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
        "write_to_stdout": False, # print changed text to stdout
        "in_place": True, # make changes to files instead of printing diffs
        "remove_all_unused_imports": False,
        "ignore_init_module_imports": False,  # exclude __init__.py when removing unused imports
        "expand_star_imports": False,
        "remove_duplicate_keys": False,
        "remove_unused_variables": False,  # remove all unused imports (not just those from the standard library)
        "remove_rhs_for_unused_variables": False,
        "ignore_pass_statements": True,
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


# def run_autoflake_old(path: Path, capture_output: bool = False, process_pyi: bool = False):
#     """
#     run autoflake to remove unused imports
#     needs to be run BEFORE black otherwise it does not recognize long import from`s.
#     note: is run file-by-file to include processing .pyi files
#     """
#     ret = 0
#     autoflake_cmd = [
#         "autoflake",
#         "-r",
#         "--in-place",
#         # "--remove-all-unused-imports",
#         # "--ignore-init-module-imports",
#         path.as_posix(),
#         "-v",
#         "-v",  # show some feedback
#     ]
#     log.debug("Running autoflake on: {}".format(path))
#     # subprocess.run(cmd, capture_output=log.level >= logging.INFO)
#     result = subprocess.run(autoflake_cmd, capture_output=capture_output, shell=False)
#     if result.returncode != 0:  # pragma: no cover
#         # retry with shell=True
#         result = subprocess.run(autoflake_cmd, capture_output=capture_output, shell=True)
#         if result.returncode != 0:  # pragma: no cover
#             log.warning(f"autoflake failed on: {path}")
#             ret = result.returncode

#     if process_pyi:
#         for file in list(path.rglob("*.pyi")):
#             autoflake_cmd = [
#                 "autoflake",
#                 "-r",
#                 "--in-place",
#                 # "--remove-all-unused-imports",
#                 # "--ignore-init-module-imports",
#                 file.as_posix(),
#                 "-v",
#                 "-v",  # show some feedback
#             ]
#             log.trace("Running autoflake on: {}".format(path))
#             # subprocess.run(cmd, capture_output=log.level >= logging.INFO)
#             result = subprocess.run(autoflake_cmd, capture_output=capture_output)
#             if result.returncode != 0:
#                 log.warning(f"autoflake failed on: {file}")
#                 ret = result.returncode

#     return ret
