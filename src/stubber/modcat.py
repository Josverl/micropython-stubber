"""
Used to define where stub modules should and should not be copied to, or merged to 

This is shared between stubber, and external build scripts.
"""
from __future__ import annotations

from typing import Final

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
    # time ( should be in stdlib - but has implementation differences per port)
    # Experiment
    "os",  # TODO # Do not remove `os` to allow better typing by mypy for the `os` module
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
        # "collections",  # must be in stdlib
        # "types",  # must be in stdlib
        # "abc",  # must be in stdlib
        "time",  # used from merged ( should be in stdlib - but has implementation differences per port)
        # "io",  # must be in stdlib
    ] + STDLIB_ONLY_MODULES,
    StubSource.FIRMWARE: [
        "builtins",
        # "collections",  # collections must be in stdlib
    ] + STDLIB_ONLY_MODULES,
    StubSource.MERGED: STDLIB_ONLY_MODULES,
}

# these modules will be replaced by a simple import statement to import from stdlib
STDLIB_UMODULES = ["ucollections"]

########################################################
# stubber.rst...                                       #
########################################################
U_MODULES = [
    "array",
    "asyncio",
    "binascii",
    "io",
    "json",
    "machine",
    "os",
    "select",
    "ssl",
    "struct",
    "socket",
    "time",
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
    "asyncio", # just for documentation 
    # stdlib stubs are using the version from stdlib/asyncio
    "rp2/PIOASMEmit.pyi",
    "rp2/asm_pio.pyi",
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
        "types", # defined in webassembly pyscript - shadows stdlib
        "abc", # defined in webassembly pyscript - shadows stdlib
        # "uos", # ???? problems with mypy & webassembly stubs 
    ]
    + STDLIB_ONLY_MODULES
    + [f"u{mod}" for mod in U_MODULES]
)
"Modules to remove from merged stubs, U_MODULES will be recreated later"

