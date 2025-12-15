"""Enumerations for the stubber package."""

from enum import Enum


class StubSource(str, Enum):
    # NOTE: The literal values are persisted (e.g., databases/manifests). "MCU stubs" must remain unchanged.
    FIRMWARE = "MCU stubs"
    "stubs built by combining firmware-derived stubs (also referred to as firmware stubs), frozen, and core stubs"
    FROZEN = "Frozen stubs"
    "stubs of python modules that are frozen as part of the firmware image"
    CORE = "Core stubs"
    "stubs that allow (some) MicroPython code to be run by CPython"
    DOC = "Doc stubs"
    "stubs built by parsing the micropython RST documentation files"
    MERGED = "Merged stubs"
    "stubs built by merging the information from doc-stubs and firmware stubs"

    def __str__(self):
        # Always force string values
        return self.value

    def __repr__(self):
        # Always force string values
        return self.value
