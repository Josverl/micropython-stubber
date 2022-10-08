from collections import namedtuple
import pytest

UName = namedtuple("UName", ["sysname", "nodename", "release", "version", "machine"])

LOCATIONS = ["board", pytest.param("minified", marks=pytest.mark.minified)]
VARIANTS = ["createstubs", "createstubs_mem", "createstubs_db"]
