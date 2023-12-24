"""Test publish module"""
from pathlib import Path
import pytest
from mock import MagicMock
from pytest_mock import MockerFixture

from stubber.publish.publish import build_multiple

from .fakeconfig import FakeConfig

ALL_PUBLISH_RESULTS = {"Published to PyPi", "Published to Test-PyPi", "Build successful", "-"}


@pytest.mark.mocked
@pytest.mark.integration
def test_build_no_change(mocker: MockerFixture, tmp_path: Path, pytestconfig: pytest.Config):
    """Test build_multiple"""
    # test requires that the stubs are cloned locally
    if not (pytestconfig.rootpath / "repos/micropython-stubs").exists():
        pytest.skip("Integration test: micropython-stubs repo not found")

    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.publish.CONFIG", config)
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)
    m_is_changed: MagicMock = mocker.patch("stubber.publish.package.StubPackage.is_changed", autospec=True, return_value=False)  # type: ignore

    m_check: MagicMock = mocker.patch("stubber.publish.package.StubPackage.check", autospec=True, return_value=True)  # type: ignore
    m_p_build: MagicMock = mocker.patch(
        "stubber.publish.package.StubPackage.poetry_build", autospec=True, return_value=True
    )
    m_p_publish: MagicMock = mocker.patch(
        "stubber.publish.package.StubPackage.poetry_publish", autospec=True, return_value=True
    )

    # -----------------------------------------------------------------------------------------------
    # Test build: not changed :--> should not build or publish
    # -----------------------------------------------------------------------------------------------
    result = build_multiple(production=False, ports=["stm32"])
    assert len(result) > 0
    assert m_p_build.call_count == 0
    assert m_p_publish.call_count == 0


@pytest.mark.mocked
@pytest.mark.integration
def test_build_changed(mocker: MockerFixture, tmp_path: Path, pytestconfig: pytest.Config):
    """Test build_multiple"""
    # test requires that the stubs are cloned locally
    if not (pytestconfig.rootpath / "repos/micropython-stubs").exists():
        pytest.skip("Integration test: micropython-stubs repo not found")

    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.publish.CONFIG", config)
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)
    m_is_changed: MagicMock = mocker.patch(
        "stubber.publish.package.StubPackage.is_changed", autospec=True, return_value=False
    )

    m_check: MagicMock = mocker.patch("stubber.publish.package.StubPackage.check", autospec=True, return_value=True)  # type: ignore
    m_p_build: MagicMock = mocker.patch(
        "stubber.publish.package.StubPackage.poetry_build", autospec=True, return_value=True
    )
    m_p_publish: MagicMock = mocker.patch(
        "stubber.publish.package.StubPackage.poetry_publish", autospec=True, return_value=True
    )

    # -----------------------------------------------------------------------------------------------
    # Test publish - changed :--> should build and publish
    # -----------------------------------------------------------------------------------------------
    m_is_changed.return_value = True
    result = build_multiple(production=False, ports=["stm32"], versions=["latest"])
    assert len(result) > 0
    assert m_p_build.call_count >= 1
    assert m_p_publish.call_count == 0


@pytest.mark.mocked
@pytest.mark.integration
def test_build_force(mocker: MockerFixture, tmp_path: Path, pytestconfig: pytest.Config):
    """Test build_multiple"""
    # test requires that the stubs are cloned locally
    if not (pytestconfig.rootpath / "repos/micropython-stubs").exists():
        pytest.skip("Integration test: micropython-stubs repo not found")

    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.publish.CONFIG", config)
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)
    m_is_changed: MagicMock = mocker.patch(
        "stubber.publish.package.StubPackage.is_changed", autospec=True, return_value=False
    )

    m_check: MagicMock = mocker.patch(
        "stubber.publish.package.StubPackage.check", autospec=True, return_value=True
    )
    m_p_build: MagicMock = mocker.patch(
        "stubber.publish.package.StubPackage.poetry_build", autospec=True, return_value=True
    )
    m_p_publish: MagicMock = mocker.patch(
        "stubber.publish.package.StubPackage.poetry_publish", autospec=True, return_value=True
    )

    # -----------------------------------------------------------------------------------------------
    # Test publish - not changed + Force :--> should build and publish
    m_p_build.reset_mock()
    m_check.reset_mock()
    m_p_publish.reset_mock()
    m_is_changed.reset_mock()
    # -----------------------------------------------------------------------------------------------
    m_is_changed.return_value = False
    result = build_multiple(production=False, force=True, ports=["stm32"], versions=["latest"])
    assert len(result) > 0
    assert m_p_build.call_count >= 1
    assert m_p_publish.call_count == 0
