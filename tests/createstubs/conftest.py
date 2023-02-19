from collections import namedtuple
import pytest
from importlib import import_module

UName = namedtuple("UName", ["sysname", "nodename", "release", "version", "machine"])

LOCATIONS = ["board", pytest.param("minified", marks=pytest.mark.minified)]
VARIANTS = ["createstubs", "createstubs_mem", "createstubs_db"]


def import_variant(location: str, variant: str, minified: bool = False):
    # sourcery skip: assign-if-exp
    """Import the variant module and return it."""
    if location == "minified":
        minified = True
    if minified:
        mod_name = f".board.{variant}_min"
    else:
        mod_name = f".board.{variant}"
    return import_module(mod_name, "stubber")  # type: ignore
