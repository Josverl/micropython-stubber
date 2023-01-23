"""Enumerations for the stubber package."""
from enum import Enum


class StubSource(str, Enum):
    FIRMWARE = "Firmware stubs"
    "stubs built by combining the firmware, frozen and core stubs"
    FROZEN = "Frozen stubs"
    "stubs of python modules that are frozen as part of the firmware image"
    CORE = "Core stubs"
    "stubs that allow (some) MicroPython code to be run by CPython"
    DOC = "Doc stubs"
    "stubs built by parsing the micropython RST documentation files"
    MERGED = "Merged stubs"
    "stubs built by merging the information from doc-stubs and firmware-stubs"


ALL_TYPES = ["combo", "doc", "core", "firmware"]
COMBO_STUBS = ALL_TYPES[0]
DOC_STUBS = ALL_TYPES[1]
CORE_STUBS = ALL_TYPES[2]
FIRMWARE_STUBS = ALL_TYPES[3]

