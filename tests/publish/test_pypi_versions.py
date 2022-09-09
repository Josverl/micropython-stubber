import pytest
import stubber.publish.pypi as pypi
from packaging.version import Version, parse
from stubber.publish.pypi import get_pypy_versions


def test_get_pypy_versions2():
    pass


def test_get_pypy_versions():
    versions = get_pypy_versions("micropython-esp32-stubs", production=False)
    assert isinstance(versions, list)
    assert len(versions) > 0
    assert isinstance(versions[0], Version)

    versions = get_pypy_versions("micropython-esp32-stubs", base=Version("1.18"))
    assert isinstance(versions, list)
    assert len(versions) > 0
    assert isinstance(versions[0], Version)

    versions = get_pypy_versions("I-do-not-exist-for-sure")
    assert isinstance(versions, list)
    assert len(versions) == 0
