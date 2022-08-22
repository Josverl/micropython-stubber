from pathlib import Path

import pytest
from pysondb import PysonDB
from stubber.publish.publish_stubs import (ALL_TYPES, COMBINED, CORE_STUBS,
                                           DOC_STUBS, get_database,
                                           get_package, package_name)


# test generation of different package names
@pytest.mark.parametrize(
    "family, pkg, port, board, expected",
    [
        ("micropython", COMBINED, "esp32", "GENERIC", "micropython-esp32-stubs"),
        ("micropython", COMBINED, "esp32", "TINY", "micropython-esp32-tiny-stubs"),
        ("micropython", DOC_STUBS, "esp32", None, "micropython-doc-stubs"),
        ("micropython", DOC_STUBS, "esp32", "GENERIC", "micropython-doc-stubs"),
        ("micropython", CORE_STUBS, None, None, "micropython-core-stubs"),
        ("micropython", CORE_STUBS, None, None, "micropython-core-stubs"),
        ("pycom", CORE_STUBS, None, None, "pycom-core-stubs"),
    ],
)
def test_package_name(family, pkg, port, board, expected):
    x = package_name(family=family, pkg=pkg, port=port, board=board)
    assert x == expected


# test get package from database
@pytest.mark.parametrize(
    "package_name, version, present",
    [
        ("micropython-esp32-stubs", "1.18", True),
        ("micropython-stm32-stubs", "1.17", True),
        ("micropython-doc-stubs", "1.10", False),
        ("pycopy-foo-stubs", "1.18", False),
    ],
)
def test_get_package(package_name, version, present):
    # TODO: use test database with known content
    # Cache database in memory?
    db = get_database("/develop/MyPython/micropython-stubs/publish", production=False)
    pkg = get_package(db, Path("foo"), pkg_name=package_name, mpy_version=version)
    if present:
        assert pkg
        assert pkg["name"] == package_name
        assert pkg["mpy_version"] == version
        assert len(pkg["path"]) > 0
        assert len(pkg["pkg_version"]) > 0
        assert len(pkg["hash"]) > 0
        assert len(pkg["description"]) > 0
        assert len(pkg["stub_sources"]) > 0
    else:
        assert pkg == None
