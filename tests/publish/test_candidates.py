"""Test candidates.py"""
from pathlib import Path
from typing import Generator
import pytest

from stubber.publish.candidates import COMBO_STUBS, DOC_STUBS, docstub_candidates, frozen_candidates, subfolder_names, version_candidates
from stubber.publish.publish import build_worklist


def test_subfoldernames(tmp_path, pytestconfig):
    # test data
    path = pytestconfig.rootpath / "tests/publish/data/stub-version"
    names = subfolder_names(path)
    assert isinstance(names, Generator)
    l = list(names)
    assert len(l) > 6


@pytest.mark.parametrize("suffix,count", [("frozen", 5), ("docstubs", 2)])
def test_version_candidates(pytestconfig, suffix, count):
    # test data
    path: Path = pytestconfig.rootpath / "tests/publish/data/stub-version"
    versions = version_candidates(suffix, path=path)
    assert isinstance(versions, Generator)
    l = list(versions)
    assert len(l) == count


@pytest.mark.parametrize("prefix, suffix,count", [("foobar", "frozen", 1)])
def test_version_prefix(pytestconfig, prefix, suffix, count):
    # test data
    path: Path = pytestconfig.rootpath / "tests/publish/data/stub-version"
    versions = version_candidates(prefix=prefix, suffix=suffix, path=path)
    assert isinstance(versions, Generator)
    l = list(versions)
    assert len(l) == count


@pytest.mark.parametrize(
    "family, versions, count",
    [
        ("micropython", "latest", 1),
        ("micropython", "v1.18", 1),
        ("micropython", "1.18", 1),
        ("micropython", "auto", 2),
    ],
)
def test_docstub_candidates(pytestconfig, family, versions, count):
    # test data
    path: Path = pytestconfig.rootpath / "tests/publish/data/stub-version"
    docstubs = docstub_candidates(path=path, family=family, versions=versions)
    assert isinstance(docstubs, Generator)
    l = list(docstubs)
    assert len(l) == count
    if len(l) > 0:
        assert l[0]["pkg_type"] == DOC_STUBS


@pytest.mark.parametrize(
    "family, versions, ports, boards, count",
    [
        ("foobar", "auto", "foo", "bar", 2),  # self + Generic
        ("foobar", "auto", "foo", "not", 1),  # generic
        # find all candidates
        ("micropython", "auto", "auto", "auto", 19),
        # list GENERIC boards for any version (case sensitive on linux/mac)
        ("micropython", "auto", "auto", "GENERIC", 11),
        ("micropython", "latest", "auto", "auto", 7),
        ("micropython", "v1.16", "foo", "GENERIC", 0),  # port folder does not exist
        # list GENERIC boards for specific version (case sensitive on linux/mac)
        ("micropython", "v1.18", "auto", "GENERIC", 3),
        ("micropython", "v1.18", "esp32", "auto", 2),
        ("micropython", "v1.18", "esp32", "GENERIC", 1),
        ("micropython", "v1.18", "stm32", "GENERIC", 1),
        # list borads for specific port
        ("micropython", "v1.18", "stm32", "auto", 2),
        # list all ports / boards for a version
        ("micropython", "v1.18", "auto", "auto", 5),
        ("micropython", "v1.18", "stm32", "PYBD_SF2", 2),  # Self + Generic
    ],
)
def test_frozen_candidates(pytestconfig, family, versions, ports, boards, count):
    # test data
    path = pytestconfig.rootpath / "tests/publish/data/stub-version"
    frozen = frozen_candidates(path=path, family=family, versions=versions, ports=ports, boards=boards)
    assert isinstance(frozen, Generator)
    l = list(frozen)
    print()
    for i in l:
        print(i)
    assert len(l) == count, f"{len(l)} != {count}, {l}"
    if len(l) > 0:
        assert l[0]["pkg_type"] == COMBO_STUBS


@pytest.mark.parametrize(
    "family, versions, ports, boards, count",
    [
        # find no candidates
        ("nono", "auto", "auto", "auto", 0),
        # find all candidates
    ],
)
@pytest.mark.skip("WIP")
def test_frozen_candidates_err(pytestconfig, family, versions, ports, boards, count):
    # test data
    path = pytestconfig.rootpath / "tests/publish/data/stub-version"
    with pytest.raises(Exception) as exc_info:
        _ = frozen_candidates(path=path, family=family, versions=versions, ports=ports, boards=boards)
    assert exc_info.type == NotImplementedError

@pytest.mark.parametrize(
    "family, versions, ports, boards, count",
    [
        ("nono", "auto", "auto", "auto", 0),  # find no candidates
        ("nono", "auto", "auto", "auto", 0),  # find no candidates
        ("micropython", "v1.18", "auto", "GENERIC", 17), # find v1.18 ports
        ("micropython", "v1.18", "esp32", "GENERIC", 1), # find v1.18 ESP32 ports 
        ("micropython", "v1.19.1", "esp8266", "GENERIC", 1), # find v1.18 ESP8266 ports 
        ("micropython", "v1.18", "stm32", "auto", 56), # find v1.18 STM32 boards
        ("micropython", "v1.18", "auto", "auto", 140), # find all v1.18 ports & boards
        ("micropython", "v1.18", "auto", "NUCLEO_F091RC", 1), # find v1.18 NUCLEO_F091RC boards
        ("micropython", ["v1.18"], "auto", "NUCLEO_F091RC", 1), # find v1.18 NUCLEO_F091RC boards
        ("micropython", ["latest"], "auto", "NUCLEO_F091RC", 1), # find v1.18 NUCLEO_F091RC boards
        ("micropython", ["latest","v1.18"], "auto", "NUCLEO_F091RC", 2), # find v1.18 NUCLEO_F091RC boards
    ],
)
def test_worklist(family, versions, ports, boards, count):
    wl = build_worklist(family=family, versions=versions, ports=ports, boards=boards)
    assert isinstance(wl, list)
    assert len(wl) == count


