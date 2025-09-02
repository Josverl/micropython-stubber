"""Enumerations for the stubber package."""
from enum import Enum


class StubSource(str, Enum):
    FIRMWARE = "MCU stubs"
    "stubs built by combining the firmware, frozen and core stubs"
    FROZEN = "Frozen stubs"
    "stubs of python modules that are frozen as part of the firmware image"
    CORE = "Core stubs"
    "stubs that allow (some) MicroPython code to be run by CPython"
    DOC = "Doc stubs"
    "stubs built by parsing the micropython RST documentation files"
    MERGED = "Merged stubs"
    "stubs built by merging the information from doc-stubs and MCU stubs"

    def __str__(self):
        # Always force string values
        return self.value

    def __repr__(self):
        # Always force string values
        return self.value

