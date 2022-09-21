
import pytest
from mock import MagicMock
from packaging.version import Version
from pytest_mock import MockerFixture
from stubber.publish.publish import publish_multiple, publish_one

from .fakeconfig import FakeConfig

# @pytest.mark.parametrize(
#     "pkg_type, ports, boards, versions",
#     [
#         (COMBO_STUBS, ["esp32"], ["GENERIC"], ["1.18"]),
#         (DOC_STUBS, [], [], ["1.18"]),
#     ],
# )


@pytest.mark.parametrize(
    "production, dryrun, check_cnt, build_cnt, publish_cnt",
    [
        (True, True, 1, 1, 0),
        (True, False, 1, 1, 1),
        (False, True, 1, 1, 0),
        (False, False, 1, 1, 1),
    ],
)
@pytest.mark.mocked
def test_publish_one(mocker:MockerFixture, tmp_path, pytestconfig, production: bool, dryrun: bool, check_cnt: int, build_cnt: int, publish_cnt: int):
    """Test publish_multiple"""
    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    # need to use fake config in two places
    mocker.patch("stubber.publish.publish.CONFIG", config)
    mocker.patch("stubber.publish.stubpacker.CONFIG", config)

    m_check: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.check", autospec=True, return_value=True)
    m_build: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.build", autospec=True, return_value=True)
    m_publish: MagicMock = mocker.patch("stubber.publish.stubpacker.StubPackage.publish", autospec=True, return_value=True)

    result = publish_one(production=production, dryrun=dryrun, frozen=True, ports="esp32", boards="GENERIC", versions="1.18")
    assert result
    assert m_check.call_count == check_cnt
    assert m_build.call_count == build_cnt
    assert m_publish.call_count == publish_cnt
    assert result["result"] in ["Published", "DryRun successful"]
    assert Version(result["version"]).base_version == Version("1.18").base_version

@pytest.mark.mocked
def test_publish_multiple(mocker, tmp_path, pytestconfig):
    """Test publish_multiple"""
    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.publish.CONFIG", config)
    mocker.patch("stubber.publish.stubpacker.CONFIG", config)

    m_check: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.check", autospec=True, return_value=True)
    m_build: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.build", autospec=True, return_value=True)
    m_publish: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.publish", autospec=True, return_value=True)

    result = publish_multiple(production=False, frozen=True, dryrun=True)
    result = publish_multiple(production=False, frozen=True, dryrun=False)

    assert m_build.call_count >= 2
    assert m_publish.call_count >= 2


@pytest.mark.mocked
def test_publish_prod(mocker, tmp_path, pytestconfig):
    """Test publish_multiple"""

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

    result = publish_one(production=production, dryrun=dryrun, frozen=True, ports="esp32", boards="GENERIC", versions="1.18")
    assert result
    assert result["result"] in ["Published", "DryRun successful"]
    assert Version(result["version"]).base_version == Version("1.18").base_version

    assert Version(result["version"]) == Version("1.18.post43")
