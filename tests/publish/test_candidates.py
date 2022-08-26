from pathlib import Path
from typing import Generator

import pytest
from stubber.publish.candidates import (
    COMBO_STUBS,
    CORE_STUBS,
    DOC_STUBS,
    docstub_candidates,
    frozen_candidates,
    subfolder_names,
    version_cadidates,
)


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
    versions = version_cadidates(suffix, path=path)
    assert isinstance(versions, Generator)
    l = list(versions)
    assert len(l) == count


@pytest.mark.parametrize("prefix, suffix,count", [("foobar", "frozen", 1)])
def test_version_prefix(pytestconfig, prefix, suffix, count):
    # test data
    path: Path = pytestconfig.rootpath / "tests/publish/data/stub-version"
    versions = version_cadidates(prefix=prefix, suffix=suffix, path=path)
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
        ("micropython", "latest", "auto", "auto", 12),
        ("micropython", "v1.18", "auto", "auto", 6),
        ("micropython", "v1.18", "esp32", "auto", 3),
        ("micropython", "v1.18", "auto", "GENERIC", 2),
        ("micropython", "v1.18", "auto", "generic", 2),
        ("micropython", "v1.18", "esp32", "generic", 1),
        ("micropython", "v1.00", "esp32", "generic", 1),
        ("foobar", "auto", "foo", "bar", 1),
        ("nono", "auto", "auto", "auto", 0),
        ("micropython", "auto", "auto", "auto", 48),
    ],
)
def test_frozen_candidates(pytestconfig, family, versions, ports, boards, count):
    # test data
    path = pytestconfig.rootpath / "tests/publish/data/stub-version"
    frozen = frozen_candidates(path=path, family=family, versions=versions, ports=ports, boards=boards)
    assert isinstance(frozen, Generator)
    l = list(frozen)
    assert len(l) == count, f"{len(l)} != {count}, {l}"
    if len(l) > 0:
        assert l[0]["pkg_type"] == COMBO_STUBS


# def publish(family, port, board, version, pkg_type, comment="-->", **kwargs):
#     print(pkg_type, family, version, port, board, comment)


# for todo in chain(
#     gen_frozen_list(versions="1.19", ports=["esp32"], boards=["wipy"]),
#     gen_frozen_list(versions="latest"),
#     gen_docstub_list(versions="1.19"),
# ):
#     publish(**todo)
