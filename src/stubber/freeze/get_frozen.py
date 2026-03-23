#!/usr/bin/env python3
"""
Collect modules and python stubs from MicroPython source projects (v1.12 +) and stores them in the all_stubs folder
The all_stubs folder should be mapped/symlinked to the micropython_stubs/stubs repo/folder

"""

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
import shutil  # start moving from os & glob to pathlib
import subprocess
from pathlib import Path
from typing import List, Optional

from mpflash.logger import log
from mpflash.versions import SET_PREVIEW, V_PREVIEW
from packaging.version import Version

from stubber import utils
from stubber.freeze.freeze_folder import freeze_folders  # Micropython < v1.12
from stubber.freeze.freeze_manifest_2 import freeze_one_manifest_2
from stubber.utils.config import CONFIG

FAMILY = "micropython"


def get_manifests(mpy_path: Path) -> List[Path]:
    """
    Returns a list of all manifests.py files found in the ports folder of the MicroPython repo
    """
    log.info(f"looking for manifests in {mpy_path}")
    all_manifests = [
        m.absolute()
        for m in (mpy_path / "ports").rglob("manifest.py")
        if Path(m).parent.name != "coverage" and "venv" not in m.parts and ".venv" not in m.parts
    ]
    log.info(f"manifests found: {len(all_manifests)}")
    return all_manifests


def add_comment_to_path(path: Path, comment: str) -> None:
    """
    Add a comment to the top of each .py and .pyi file in the path.
    Uses simple string prepending for speed and reliability.
    """
    count = 0
    failed_files = []
    
    # Ensure comment starts with # and ends with newline
    if not comment.startswith("#"):
        comment = f"# {comment}"
    if not comment.endswith("\n"):
        comment = f"{comment}\n"
    
    # Process both .py and .pyi files
    for pattern in ("*.py", "*.pyi"):
        for stub_file in sorted(path.rglob(pattern)):
            rel_path = stub_file.relative_to(path)
            try:
                content = stub_file.read_text(encoding="utf-8")
                
                # Skip if comment already exists (idempotent check)
                # Check first non-empty line to handle whitespace variations
                lines = content.split('\n', 5)  # Only check first few lines for efficiency
                first_non_empty = next((line for line in lines if line.strip()), '')
                if first_non_empty.strip() == comment.strip():
                    log.trace(f"  - Comment already in {rel_path}")
                    continue
                
                # Simple prepend - fast and reliable
                new_content = comment + content
                stub_file.write_text(new_content, encoding="utf-8")
                count += 1
                log.debug(f"  ✓ Added comment to {rel_path}")
                
            except (OSError, UnicodeDecodeError) as e:
                log.warning(f"Could not add comment to {rel_path}: {type(e).__name__}: {e}")
                failed_files.append((stub_file, f"{type(e).__name__}"))
    
    log.info(f"Successfully added comment to {count} file(s) in {path}")
    if failed_files:
        log.warning(f"Failed to process {len(failed_files)} file(s):")
        for file, reason in failed_files:
            log.warning(f"  - {file.relative_to(path)}: {reason}")


def freeze_any(
    stub_folder: Optional[Path] = None,
    version: str = V_PREVIEW,
    mpy_path: Optional[Path] = None,
    mpy_lib_path: Optional[Path] = None,
) -> Path:
    """
    Get and parse the to-be-frozen .py modules for micropython to extract the static type information
     - requires that the MicroPython and Micropython-lib repos are checked out and available on a local path
     - repos should be cloned side-by-side as some of the manifests refer to micropython-lib scripts using a relative path

    The micropython-* repos must be checked out to the required version/tag.

    """
    count = 0
    current_dir = os.getcwd()
    mpy_path = Path(mpy_path).absolute() if mpy_path else CONFIG.mpy_path.absolute()
    mpy_lib_path = Path(mpy_lib_path).absolute() if mpy_lib_path else CONFIG.mpy_path.absolute()

    # if old version of micropython, use the old freeze method
    if version not in SET_PREVIEW and Version(version) <= Version("1.11"):
        frozen_stub_path = get_fsp(version, stub_folder)
        log.debug("MicroPython v1.11, older or other")
        # others
        modules = freeze_folders(
            frozen_stub_path.as_posix(),
            mpy_path.as_posix(),
            mpy_lib_path.as_posix(),
            version,
        )
        count = len(modules)
    else:
        # get the current checked out version
        version = utils.checkedout_version(CONFIG.mpy_path)

        frozen_stub_path = get_fsp(version, stub_folder)
        # get the manifests of the different ports and boards
        all_manifests = get_manifests(mpy_path)

        # process all_manifests under the ports folder and update the frozen files in the stubs folder
        # we are going to jump around, avoid relative paths
        mpy_path = mpy_path.absolute()
        mpy_lib_path = mpy_lib_path.absolute()

        if len(all_manifests) > 0:
            log.info(f"manifests: {len(all_manifests)}")
            shutil.rmtree(frozen_stub_path, ignore_errors=True)
        else:
            log.warning("no manifests found")
        for manifest in all_manifests:
            try:
                freeze_one_manifest_2(manifest, frozen_stub_path, mpy_path, mpy_lib_path, version)
                count += 1
            except Exception as e:
                log.error(f"Error processing manifest {manifest} : {e}")

    # add comment line to each file with the micropython version it was generated from
    add_comment_to_path(frozen_stub_path, f"# Micropython {version} frozen stubs")

    # restore cwd
    os.chdir(current_dir)
    return frozen_stub_path


def get_fsp(version: str, stub_folder: Optional[Path] = None) -> Path:
    """get frozen stub path"""
    if not stub_folder:
        frozen_stub_path = CONFIG.stub_path / f"{FAMILY}-{utils.clean_version(version, flat=True)}-frozen"
        frozen_stub_path = frozen_stub_path.absolute()
    else:
        frozen_stub_path: Path = Path(stub_folder).absolute()
    return frozen_stub_path
