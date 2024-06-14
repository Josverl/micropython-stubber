import pytest
from packaging.version import Version

from stubber.publish.pypi import get_pypi_versions

pytestmark = [pytest.mark.stubber]


def test_get_pypi_versions():  # sourcery skip: extract-duplicate-method
    versions = get_pypi_versions("micropython-esp32-stubs", production=False)
    assert isinstance(versions, list)
    assert len(versions) > 0
    assert isinstance(versions[0], Version)

    # FIXME : dependency on accesibility of (test.)pypi.org
    versions = get_pypi_versions("micropython-esp32-stubs", base=Version("1.18"))
    assert isinstance(versions, list)
    assert len(versions) > 0
    assert isinstance(versions[0], Version)

    versions = get_pypi_versions("I-do-not-exist-for-sure")
    assert isinstance(versions, list)
    assert len(versions) == 0
