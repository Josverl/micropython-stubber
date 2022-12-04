from pathlib import Path
import pytest
from mock import MagicMock
from packaging.version import Version
from pytest_mock import MockerFixture
from stubber.publish.merge_docstubs import merge_all_docstubs, copy_docstubs

from .fakeconfig import FakeConfig


@pytest.mark.mocked
def test_merge_all_docstubs_mocked(mocker, tmp_path, pytestconfig):
    """Test publish_multiple"""
    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.merge_docstubs.CONFIG", config)

    m_firmware_candidates: MagicMock = mocker.patch(
        "stubber.publish.merge_docstubs.firmware_candidates",
        autospec=True,
        return_value=[
            {"family": "micropython", "version": "1.19.1", "port": "stm32", "board": "GENERIC"},
            {"family": "micropython", "version": "1.19.1", "port": "esp32", "board": "GENERIC"},
        ],
    )
    m_copy_docstubs: MagicMock = mocker.patch("stubber.publish.merge_docstubs.copy_docstubs", autospec=True)

    result = merge_all_docstubs(["v1.18", "v1.19"])

    assert m_firmware_candidates.call_count == 1
    assert m_copy_docstubs.call_count == 2


@pytest.mark.mocked
def test_copydocstubs_mocked(mocker, tmp_path, pytestconfig):
    """Test publish_multiple"""
    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.merge_docstubs.CONFIG", config)

    m_enrich_folder: MagicMock = mocker.patch("stubber.publish.merge_docstubs.enrich_folder", autospec=True, return_value=42)
    m_copytree: MagicMock = mocker.patch("stubber.publish.merge_docstubs.shutil.copytree", autospec=True)
    m_copy: MagicMock = mocker.patch("stubber.publish.merge_docstubs.shutil.copy", autospec=True)

    # use files already in test set
    fw_path = Path(".") / "tests" / "data" / "micropython-1.18-esp32"
    docstub_path = Path(".") / "tests" / "data" / "micropython-1.18-docstubs"
    dest_path = tmp_path / "micropython-merged"
    result = copy_docstubs(fw_path, dest_path, docstub_path)

    assert result == 42
    assert m_enrich_folder.call_count == 1
    assert m_copytree.call_count == 1
    assert m_copy.call_count == 1
