from collections import namedtuple
import pytest
from importlib import import_module

UName = namedtuple("UName", ["sysname", "nodename", "release", "version", "machine"])

LOCATIONS = ["board", pytest.param("minified", marks=pytest.mark.minified)]
VARIANTS = ["createstubs", "createstubs_mem", "createstubs_db"]


def import_variant(location: str, variant: str, minified=False):
    """Import the variant module and return it."""
    # location - board / minified - ignored for now
    mod_name = f".board.{variant}"
    return import_module(mod_name, "stubber")  # type: ignore
