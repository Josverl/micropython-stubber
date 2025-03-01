"""
Merge configuration for the stubber.
defines constants and util functions to copy, update or remove type modules
"""

import shutil
from pathlib import Path
from typing import Final, List

from mpflash.logger import log
from stubber.rst.lookup import U_MODULES

EXT: Final = [".pyi", ".py", ""]
CP_REFERENCE_TO_DOCSTUB: Final = [
    "asyncio",
    "rp2/PIOASMEmit.pyi",
    "rp2/asm_pio.pyi",
]
"Modules to copy from reference modules to the docstubs"


STDLIB_MODULES: Final = [
    "collections",
    "io",
    "builtins",
    "asyncio",
    "sys",
    # "os",  # TODO # Do not remove `os` to allow better typing by mypy for the `os` module
    # "ssl",  # TODO
]
"""Modules that should be in /stdlib"""
# and should not be in the individual packes as that causes duplication

RM_MERGED: Final = (
    [
        "sys",  # use auto patched version from mpy_stdlib
        "asyncio",  # use manually patched version from  mpy_stdlib
        "_asyncio",  # ditto
        "uasyncio",  # ditto
        "_rp2",  # Leave out for now , to avoid conflicts with the rp2 module
        "pycopy_imphook",  #  pycopy only: not needed in the merged stubs
        # "os",
        "types", # defined in webassembly pyscript - shadows stdlib
        "abc", # defined in webassembly pyscript - shadows stdlib
        # "uos", # ???? problems with mypy & webassembly stubs 
    ]
    + STDLIB_MODULES
    + [f"u{mod}" for mod in U_MODULES]
)
"Modules to remove from merged stubs, U_MODULES will be recreated later"


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
