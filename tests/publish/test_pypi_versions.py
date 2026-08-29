import pytest
from packaging.version import Version
from requests.exceptions import ReadTimeout

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


@pytest.mark.mocked
def test_get_pypi_versions_continues_after_network_error(mocker):
    client = mocker.patch("stubber.publish.pypi.PyPISimple").return_value.__enter__.return_value
    client.get_project_page.side_effect = ReadTimeout("connection timed out")
    log_error = mocker.patch("stubber.publish.pypi.log.error")

    versions = get_pypi_versions("micropython-esp32-stubs")

    assert versions == []
    log_error.assert_called_once()
    assert "Continuing without remote version information" in log_error.call_args.args[0]
