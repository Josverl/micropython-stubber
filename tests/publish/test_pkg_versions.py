from typing import List

import pytest
from mock import MagicMock
from pytest_mock import MockerFixture

from stubber.publish.stubpackage import StubPackage


# -------------------------------------------------------------------
@pytest.mark.parametrize(
    "p_published, expected",
    [
        ([], "1.19.1.post1"),
        (None, "1.19.1.post1"),
        (["1.19.1.post1"], "1.19.1.post2"),
        (["1.19.1.post1", "1.19.1.post2", "1.19.1.post4"], "1.19.1.post5"),
    ],
)
@pytest.mark.mocked
def test_version_1_19_1(
    mocker: MockerFixture,
    fake_package: StubPackage,
    p_published: List[str],
    expected: str,
):
    return _tst_version(mocker, fake_package, p_published, "1.19.1", expected)


# -------------------------------------------------------------------
@pytest.mark.version("1.20.0")
@pytest.mark.parametrize(
    "p_published, expected",
    [
        ([], "1.20.0.post1"),
        (None, "1.20.0.post1"),
        (["1.20.0.post1"], "1.20.0.post2"),
        (["1.20.0.post1", "1.20.0.post2", "1.20.0.post4"], "1.20.0.post5"),
    ],
)
@pytest.mark.mocked
def test_version_1_20_0(
    mocker: MockerFixture,
    fake_package: StubPackage,
    p_published: List[str],
    expected: str,
):
    return _tst_version(mocker, fake_package, p_published, "1.20.0", expected)


# -------------------------------------------------------------------
@pytest.mark.version("1.19.0")
@pytest.mark.parametrize(
    "p_published, expected",
    [
        ([], "1.19.0.post1"),
        (None, "1.19.0.post1"),
        (["1.19.0.post1"], "1.19.0.post2"),
        (["1.19.0.post1", "1.19.0.post2", "1.19.0.post4"], "1.19.0.post5"),
    ],
)
@pytest.mark.mocked
def test_version_1_19_0(
    mocker: MockerFixture,
    fake_package: StubPackage,
    p_published: List[str],
    expected: str,
):
    return _tst_version(mocker, fake_package, p_published, "1.19.0", expected)


# -------------------------------------------------------------------


def m_calc_hash(include_md: bool = True):
    # mock the calculation of the hashes
    if include_md:
        return "2222"
    else:
        return "1111"


def _tst_version(mocker, fake_package, p_published, p_base, expected):
    pkg = fake_package

    mocker.patch.object(pkg, "calculate_hash", side_effect=m_calc_hash, autospec=True)
    # package with a few published versions
    m_pypi_ver: MagicMock = mocker.patch("stubber.publish.stubpackage.get_pypi_versions", autospec=True, return_value=p_published)  # type: ignore
    pkg.create_update_pyproject_toml()
    pkg.mpy_version = p_base
    pkg.hash = None
    pkg.stub_hash = None

    assert pkg.is_changed(), "should be changed initially"

    next_ver = pkg.get_next_package_version()
    assert next_ver == expected
