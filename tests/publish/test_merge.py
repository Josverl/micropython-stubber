from pathlib import Path

import pytest
from mock import MagicMock

from stubber.publish.merge_docstubs import copy_and_merge_docstubs, merge_all_docstubs

from .fakeconfig import FakeConfig


@pytest.mark.mocked
@pytest.mark.integration
def test_merge_all_docstubs_mocked(mocker, tmp_path, pytestconfig):
    """Test publish_multiple"""
    if not (pytestconfig.rootpath / "repos/micropython-stubs").exists():
        pytest.skip("Integration test: micropython-stubs repo not found")

    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.merge_docstubs.CONFIG", config)

    m_board_candidates: MagicMock = mocker.patch(
        "stubber.publish.merge_docstubs.board_candidates",
        autospec=True,
        return_value=[
            {"family": "micropython", "version": "1.19.1", "port": "stm32", "board": "generic"},
            {"family": "micropython", "version": "1.19.1", "port": "esp32", "board": "generic"},
        ],
    )
    m_copy_and_merge_docstubs: MagicMock = mocker.patch(
        "stubber.publish.merge_docstubs.copy_and_merge_docstubs", autospec=True
    )
    m_add_machine_pin_call: MagicMock = mocker.patch(
        "stubber.publish.merge_docstubs.add_machine_pin_call", autospec=True
    )

    # mock pathlib.Path.exists to return True so there is no dependency of folders existing on the test system
    mocker.patch("stubber.publish.merge_docstubs.Path.exists", autospec=True, return_value=True)

    result = merge_all_docstubs(["v1.18", "v1.19"])
    assert result == 2
    assert m_board_candidates.call_count == 1
    assert m_copy_and_merge_docstubs.call_count == 2


@pytest.mark.mocked
def test_copydocstubs_mocked(mocker, tmp_path, pytestconfig):
    """Test publish_multiple"""
    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.merge_docstubs.CONFIG", config)

    m_enrich_folder: MagicMock = mocker.patch(
        "stubber.publish.merge_docstubs.enrich_folder", autospec=True, return_value=42
    )
    m_copytree: MagicMock = mocker.patch("stubber.publish.merge_docstubs.shutil.copytree", autospec=True)
    m_copy: MagicMock = mocker.patch("stubber.publish.merge_docstubs.shutil.copy", autospec=True)

    # use files already in test set
    fw_path = Path(".") / "tests" / "data" / "micropython-1.18-esp32"
    docstub_path = Path(".") / "tests" / "data" / "micropython-1.18-docstubs"
    dest_path = tmp_path / "micropython-merged"
    result = copy_and_merge_docstubs(fw_path, dest_path, docstub_path)

    assert result == 42
    assert m_enrich_folder.call_count == 1
    assert m_copytree.call_count == 1
