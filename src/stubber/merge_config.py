"""
Merge configuration for the stubber.
defines constants and util functions to copy, update or remove type modules
"""

import shutil
from pathlib import Path
from typing import List

from mpflash.logger import log

from stubber.rst.lookup import U_MODULES

EXT = [".pyi", ".py", ""]
CP_REFERENCE_TO_DOCSTUB = ["rp2/PIOASMEmit.pyi", "asyncio"]
"Modules that to copy from reference modules to the docstubs"
CP_REFERENCE_TO_MERGED = CP_REFERENCE_TO_DOCSTUB
"Modules that to copy from reference modules to the merged stubs"
RM_MERGED = ["collections", "builtins", "pycopy_imphook"]
"Modules that to remove from merged stubs"


def copy_type_modules(source_folder: Path, target_folder: Path, CP_REFERENCE_MODULES: List[str]):
    log.info("Adding additional type modules to the docstubs")
    for addition in CP_REFERENCE_MODULES:
        src = source_folder / addition
        if src.exists():
            if src.is_dir():
                target = target_folder / addition
                log.info(f" - add {target}")
                shutil.copytree(src, target, dirs_exist_ok=True)
            else:
                target = target_folder / addition
                log.info(f" - add {target}")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)


def copy_to_umodules(target_folder: Path):
    log.info("Adding additional type modules to the docstubs")
    for name in U_MODULES:
        for ext in EXT:
            target = target_folder / f"{name}{ext}"
            if target.exists():
                try:
                    if target.is_dir():
                        log.info(f" - add {target}")
                        shutil.copytree(target, target_folder / f"u{name}", dirs_exist_ok=True)
                    else:
                        log.info(f" - add {target}")
                        shutil.copy2(target, target_folder / f"u{name}{ext}")

                except OSError as e:
                    log.error(f" - not found {target.relative_to(target_folder)}, {e}")


def remove_modules(target_folder: Path, RM_MODULES: List[str]):
    log.info("Removing modules from the merged stubs")

    for name in RM_MODULES:
        for ext in EXT:
            target = target_folder / f"{name}{ext}"
            if target.exists():
                try:
                    if target.is_dir():
                        log.info(f" - remove {target}")
                        shutil.rmtree(target)
                    else:
                        log.info(f" - remove {target}")
                        target.unlink()
                finally:
                    log.debug(f" - remove {target}")
