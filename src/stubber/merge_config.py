"""
Merge configuration for the stubber.
util functions to copy, update or remove type modules
"""

import shutil
from pathlib import Path
from typing import Final, List

from mpflash.logger import log

from stubber.modcat import (CP_REFERENCE_TO_DOCSTUB, RM_MERGED,
                            STDLIB_ONLY_MODULES, U_MODULES)

EXT: Final = [".pyi", ".py", ""]


def copy_type_modules(source_folder: Path, target_folder: Path, CP_REFERENCE_MODULES: List[str]):
    log.info("Adding additional type modules:")
    for addition in CP_REFERENCE_MODULES:
        src = source_folder / addition
        if src.exists():
            if src.is_dir():
                target = target_folder / addition
                log.debug(f" - add {target}")
                shutil.copytree(src, target, dirs_exist_ok=True)
            else:
                target = target_folder / addition
                log.debug(f" - add {target}")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)


def recreate_umodules(target_folder: Path):
    log.info("create umodules to refer to modules in the merged stubs")
    # Just `create an import * from module` in the umodule.pyi
    for name in U_MODULES:
        # delete complex or simple umodule
        uname = target_folder / f"u{name}"
        try:
            if uname.exists():
                if uname.is_dir():
                    log.debug(f" - remove {uname}")
                    shutil.rmtree(uname)
                else:
                    log.debug(f" - remove {uname}")
                    uname.unlink()
            else:
                uname = uname.with_suffix(".pyi")
                if uname.exists():
                    log.debug(f" - remove {uname}")
                    uname.unlink()
        except OSError as e:
            log.error(f"Error removing {uname}: {e}")
            continue

        uname = target_folder / f"u{name}.pyi"
        with uname.open("w") as f:
            f.write(f"# This umodule is a MicroPython reference to {name}\n")
            f.write(f"from {name} import *\n")
        log.debug(f" - recreated {uname.name}")


def remove_modules(target_folder: Path, RM_MODULES: List[str]):
    log.info("Removing modules from the merged stubs")

    for name in RM_MODULES:
        for ext in EXT:
            target = target_folder / f"{name}{ext}"
            if target.exists():
                try:
                    if target.is_dir():
                        log.debug(f" - remove {target}")
                        shutil.rmtree(target)
                    else:
                        log.debug(f" - remove {target}")
                        target.unlink()
                finally:
                    log.debug(f" - remove {target}")

