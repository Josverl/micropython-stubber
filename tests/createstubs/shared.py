from importlib import import_module

import pytest

LOCATIONS = ["board", pytest.param("minified", marks=pytest.mark.minified)]
VARIANTS = ["createstubs", "createstubs_mem", "createstubs_db"]


def import_variant(location: str, variant: str, minified: bool = False):
    # sourcery skip: assign-if-exp
    """Import the variant module and return it."""
    if minified or location == "minified":
        mod_name = f".board.{variant}_min"
    else:
        mod_name = f".board.{variant}"
    return import_module(mod_name, "stubber")  # type: ignore
