"""
Used to define where stub modules should and should not be copied to, or merged to

This is shared between stubber, and external build scripts.
"""

from __future__ import annotations

from typing import Dict, Final, List

from stubber.publish.enums import StubSource

########################################################
STDLIB_ONLY_MODULES = [
    "abc",
    "array",
    "collections",
    "io",
    "builtins",
    "asyncio",
    "sys",
    "types",
    "ssl",
    "os",
    # Experiment
    "json",
    "struct",
    # "socket", # should be ins tdlib - but is only available on networked boards
    # time # should be in stdlib - but has implementation differences per port)
]
"""Modules that should only be in stdlib, and not in the individual packages"""
# and should not be in the individual packes as that causes duplication


########################################################
# stubber.publish.stubpacker                           #
########################################################
# Indicates which stubs will NOT be copied from the stub sources
# and shared with multiple modules and the sdtbli build.py that is in the stubs repo
STUBS_COPY_FILTER = {
    StubSource.FROZEN: [
        "espnow",  # merged stubs + documentation of the espnow module is better than the info in the frozen stubs
        "time",  # used from merged ( should be in stdlib - but has implementation differences per port)
        "machine",  # esp32.frozen.machine.py extends the C machine module (adds PCNT etc.)
        # Complementary frozen modules are handled by COMPLEMENTARY_FROZEN_MODULES below:
        # unique new definitions from these frozen stubs are appended to the merged stub
        # instead of being skipped or overwriting the merged stub.
        # https://github.com/micropython/micropython/blob/master/ports/esp32/modules/machine.py
    ]
    + STDLIB_ONLY_MODULES,
    StubSource.FIRMWARE: [
        "builtins",
        # "collections",  # collections must be in stdlib
    ]
    + STDLIB_ONLY_MODULES,
    StubSource.MERGED: STDLIB_ONLY_MODULES,
}

COMPLEMENTARY_FROZEN_MODULES: Final[Dict[str, List[str]]] = {
    "esp32": ["machine"],
    # Add more port -> module mappings here as they are discovered
}
"""
Port-specific frozen modules that are partial/complementary implementations extending C-modules.

These frozen modules do NOT replace the full C-module stub; instead, they add new
port-specific classes/functions that are not part of the standard C implementation.
Their unique definitions are appended to the merged stub rather than being skipped entirely.

Example: ports/esp32/modules/machine.py adds the PCNT (Pulse Counter) class to the
standard machine module for ESP32.
See: https://github.com/micropython/micropython/blob/master/ports/esp32/modules/machine.py
"""

# these modules will be replaced by a simple import statement to import from stdlib
STDLIB_UMODULES = ["ucollections"]

########################################################
# stubber.rst...                                       #
########################################################
U_MODULES = [
    "array",
    "asyncio",
    "binascii",
    "bluetooth",
    "cryptolib",
    "errno",
    "hashlib",
    "heapq",
    "io",
    "json",
    "machine",
    "os",
    "platform",
    "random",
    "re",
    "select",
    "ssl",
    "struct",
    "socket",
    "sys",
    "time",
    "websocket",
    "zlib",
]
"""
List of modules that are documented with the base name only, 
but can also be imported with a `u` prefix
"""

########################################################
# stubber.merge_config                                 #
# defines constants to copy, update, remove type stubs #
########################################################

CP_REFERENCE_TO_DOCSTUB: Final = [
    "asyncio",  # just for documentation
    # stdlib stubs are using the version from stdlib/asyncio
    # Handcoded stubs for the rp2 PIO assembler
    "rp2/PIOASMEmit.pyi",
    "rp2/asm_pio.pyi",
    "rp2/asm_pio_rp2040.pyi",
    "rp2/asm_pio_rp2350.pyi",
]
"Modules to copy from reference modules to the docstubs"


RM_MERGED = (
    [
        "sys",  # use auto patched version from mpy_stdlib
        "asyncio",  # use manually patched version from  mpy_stdlib
        "_asyncio",  # ditto
        "uasyncio",  # ditto
        "_rp2",  # Leave out for now , to avoid conflicts with the rp2 module
        "pycopy_imphook",  #  pycopy only: not needed in the merged stubs
        # "os",
        "types",  # defined in webassembly pyscript - shadows stdlib
        "abc",  # defined in webassembly pyscript - shadows stdlib
        # "uos", # ???? problems with mypy & webassembly stubs
    ]
    + STDLIB_ONLY_MODULES
    + [f"u{mod}" for mod in U_MODULES]
)
"Modules to remove from merged stubs, U_MODULES will be recreated later"
