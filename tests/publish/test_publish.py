"""Test publish module"""
from pathlib import Path
import pytest
from mock import MagicMock
from packaging.version import Version
from pytest_mock import MockerFixture

from stubber.publish.publish import publish_multiple, publish_one

from .fakeconfig import FakeConfig

ALL_PUBLISH_RESULTS = {"Published to PyPi","Published to Test-PyPi", "Build successful", "-"}

@pytest.mark.parametrize(
    "production, dryrun, is_changed, check_cnt, build_cnt, publish_cnt",
    [
        # not changed
        (True, True, False, 1, 0, 0),
        (True, False, False, 1, 0, 0),
        (False, True, False, 1, 0, 0),
        (False, False, False, 1, 0, 0),
        # dryrun
        (True, True, True, 1, 1, 0),
        (False, True, True, 1, 1, 0),
        # changed
        (True, False, True, 1, 1, 1),
        (False, False, True, 1, 1, 1),
    ],
)
@pytest.mark.mocked
@pytest.mark.integration
def test_publish_one(
    mocker: MockerFixture,
    tmp_path: Path,
    pytestconfig: pytest.Config,
    production: bool,
    dryrun: bool,
    is_changed: bool,
    check_cnt: int,
    build_cnt: int,
    publish_cnt: int,
):
    """Test publish_multiple stubs of a single version"""
    # test requires that the stubs are cloned locally
    if not (pytestconfig.rootpath / "repos/micropython-stubs").exists():
        # mark test as skipped
        pytest.skip("Integration test: micropython-stubs repo not found")

    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)

    # need to use fake config in two places
    mocker.patch("stubber.publish.publish.CONFIG", config)
    mocker.patch("stubber.publish.stubpacker.CONFIG", config)

    m_check: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.check", autospec=True, return_value=True)
    m_is_changed: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.is_changed", autospec=True, return_value=is_changed)
    m_build: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.build", autospec=True, return_value=True)
    m_publish: MagicMock = mocker.patch("stubber.publish.stubpacker.StubPackage.publish", autospec=True, return_value=True)

    result = publish_one(production=production, dryrun=dryrun, frozen=True, ports="esp32", boards="GENERIC", versions="1.18")
    assert result
    assert m_check.call_count == check_cnt
    assert m_build.call_count == build_cnt
    assert m_publish.call_count == publish_cnt
    assert result["result"] in ALL_PUBLISH_RESULTS
    assert Version(result["version"]).base_version == Version("1.18").base_version


@pytest.mark.mocked
@pytest.mark.integration
def test_publish_multiple(mocker: MockerFixture, tmp_path: Path, pytestconfig : pytest.Config):
    """Test publish_multiple"""
    # test requires that the stubs are cloned locally
    if not (pytestconfig.rootpath / "repos/micropython-stubs").exists():
        pytest.skip("Integration test: micropython-stubs repo not found")

    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.publish.CONFIG", config)
    mocker.patch("stubber.publish.stubpacker.CONFIG", config)
    m_is_changed: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.is_changed", autospec=True, return_value=False)

    m_check: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.check", autospec=True, return_value=True)
    m_build: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.build", autospec=True, return_value=True)
    m_publish: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.publish", autospec=True, return_value=True)

    # Test dryrun - not changed
    result = publish_multiple(production=False, frozen=True, dryrun=True)
    assert len(result) > 0
    assert m_build.call_count == 0
    # assert m_check.call_count == 1
    assert m_publish.call_count == 0

    # Test dryrun -  changed
    m_build.reset_mock()
    m_check.reset_mock()
    m_publish.reset_mock()
    m_is_changed.reset_mock()
    m_is_changed.return_value = True    
    result = publish_multiple(production=False, frozen=True, dryrun=True)
    assert len(result) > 0
    assert m_build.call_count >= 1
    # assert m_check.call_count == 1
    assert m_publish.call_count == 0

    # Test Actual + changed
    m_build.reset_mock()
    m_check.reset_mock()
    m_publish.reset_mock()
    m_is_changed.reset_mock()
    m_is_changed.return_value = True

    result = publish_multiple(production=False, frozen=True, dryrun=False)
    assert len(result) > 0
    assert m_build.call_count >= 1
    # assert m_check.call_count == 1
    assert m_publish.call_count >= 1


@pytest.mark.integration
@pytest.mark.mocked
def test_publish_prod(mocker: MockerFixture, tmp_path: Path, pytestconfig : pytest.Config):
    """Test publish_multiple"""
    if not (pytestconfig.rootpath / "repos/micropython-stubs").exists():
        pytest.skip("Integration test: micropython-stubs repo not found")

    production: bool = True
    dryrun: bool = False
    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    # need to use fake config in two places
    mocker.patch("stubber.publish.publish.CONFIG", config)
    mocker.patch("stubber.publish.stubpacker.CONFIG", config)

    m_check: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.check", autospec=True, return_value=True)
    m_build: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.build", autospec=True, return_value=True)
    m_pypi: MagicMock = mocker.patch(
        "stubber.publish.publish.get_pypy_versions", autospec=True, return_value=[Version("1.18.post1"), Version("1.18.post42")]
    )

    m_publish: MagicMock = mocker.patch("stubber.publish.stubpacker.StubPackage.publish", autospec=True, return_value=True)
    m_is_changed: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.is_changed", autospec=True, return_value=True)
    result = publish_one(production=production, dryrun=dryrun, frozen=True, ports="esp32", boards="GENERIC", versions="1.18")

    assert result
    assert result["result"] in ALL_PUBLISH_RESULTS
    assert Version(result["version"]).base_version == Version("1.18").base_version

    assert Version(result["version"]) == Version("1.18.post43")
    assert m_check.call_count == 1
    assert m_build.call_count == 1
    assert m_pypi.call_count == 1
    assert m_publish.call_count == 1
