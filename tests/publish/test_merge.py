from pathlib import Path

import pytest
from mock import MagicMock
from stubber.publish.merge_docstubs import copy_and_merge_docstubs, merge_all_docstubs

from .fakeconfig import FakeConfig

pytestmark = [pytest.mark.stubber]


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
    m_copy_and_merge_docstubs: MagicMock = mocker.patch("stubber.publish.merge_docstubs.copy_and_merge_docstubs", autospec=True)

    # mock pathlib.Path.exists to return True so there is no dependency of folders existing on the test system
    mocker.patch("stubber.publish.merge_docstubs.Path.exists", autospec=True, return_value=True)

    result = merge_all_docstubs(["v1.18", "v1.19"])
    assert result == 2
    assert m_board_candidates.call_count == 1
    assert m_copy_and_merge_docstubs.call_count == 2


@pytest.mark.mocked
def test_merge_all_docstubs_does_not_count_enrichment_error(mocker, tmp_path, pytestconfig):
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.merge_docstubs.CONFIG", config)
    mocker.patch(
        "stubber.publish.merge_docstubs.board_candidates",
        autospec=True,
        return_value=[{"family": "micropython", "version": "1.29.0-preview", "port": "esp32", "board": "ESP32_GENERIC_C6"}],
    )
    mocker.patch("stubber.publish.merge_docstubs.Path.exists", autospec=True, return_value=True)
    mocker.patch(
        "stubber.publish.merge_docstubs.copy_and_merge_docstubs",
        autospec=True,
        side_effect=ValueError("Failed to enrich 1 file"),
    )

    result = merge_all_docstubs(versions="1.29.0-preview", ports="esp32", boards="ESP32_GENERIC_C6")

    assert result == 0


@pytest.mark.mocked
def test_merge_all_docstubs_fallback_to_generic(mocker, tmp_path, pytestconfig):
    """Test fallback to GENERIC frozen board when board-specific stubs are not found"""
    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.merge_docstubs.CONFIG", config)

    # First call (board_candidates): returns no candidates for the specific board
    m_board_candidates: MagicMock = mocker.patch(
        "stubber.publish.merge_docstubs.board_candidates",
        autospec=True,
        return_value=[],
    )

    # Second call (frozen_candidates): returns generic frozen candidates
    m_frozen_candidates: MagicMock = mocker.patch(
        "stubber.publish.merge_docstubs.frozen_candidates",
        autospec=True,
        return_value=[
            {"family": "micropython", "version": "1.19.1", "port": "nrf", "board": "generic"},
        ],
    )

    m_filter_list: MagicMock = mocker.patch(
        "stubber.publish.merge_docstubs.filter_list",
        autospec=True,
        side_effect=[[], [{"family": "micropython", "version": "1.19.1", "port": "nrf", "board": "generic"}]],
    )

    m_copy_and_merge_docstubs: MagicMock = mocker.patch("stubber.publish.merge_docstubs.copy_and_merge_docstubs", autospec=True)
    m_log_warning = mocker.patch("stubber.publish.merge_docstubs.log.warning", autospec=True)

    # mock pathlib.Path.exists to return True so there is no dependency of folders existing on the test system
    mocker.patch("stubber.publish.merge_docstubs.Path.exists", autospec=True, return_value=True)

    # mock get_frozen_board_path to return a proper path
    def mock_get_frozen_board_path(candidate):
        return config.stub_path / f"micropython-{candidate['version']}-frozen" / candidate["port"] / candidate["board"].upper()

    mocker.patch("stubber.publish.merge_docstubs.get_frozen_board_path", side_effect=mock_get_frozen_board_path)

    # Call with a specific board that's not in the candidates
    result = merge_all_docstubs(versions="1.19.1", ports="nrf", boards="PROMICRO_NRF52840")

    # Should have called board_candidates once (initial attempt)
    assert m_board_candidates.call_count == 1

    # Should have called frozen_candidates once (fallback)
    assert m_frozen_candidates.call_count == 1

    # Should have called filter_list twice
    assert m_filter_list.call_count == 2

    # Should have logged a warning about falling back
    m_log_warning.assert_called_once()
    warning_msg = m_log_warning.call_args[0][0]
    assert "No board-specific frozen stubs found" in warning_msg
    assert "PROMICRO_NRF52840" in warning_msg
    assert "Falling back to GENERIC" in warning_msg

    # Should have merged the generic stubs
    assert result == 1
    assert m_copy_and_merge_docstubs.call_count == 1


@pytest.mark.mocked
@pytest.mark.parametrize("ports, boards", [("all", "all"), ("all", "auto"), ("nrf", "all")])
def test_merge_all_docstubs_no_fallback_for_all(mocker, tmp_path, pytestconfig, ports, boards):
    """The out-of-tree fallback must NOT trigger for 'all'/'auto' boards.

    Regression: `stubber merge --port all --board all` used to treat the literal
    'all' as a board name and create bogus '<port>-all-merged' folders via the
    frozen fallback when board_candidates returned no results.
    """
    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.merge_docstubs.CONFIG", config)

    # board_candidates returns nothing (e.g. repo/version checkout produced no candidates)
    m_board_candidates: MagicMock = mocker.patch(
        "stubber.publish.merge_docstubs.board_candidates",
        autospec=True,
        return_value=[],
    )
    # frozen_candidates must NOT be called for 'all'/'auto'
    m_frozen_candidates: MagicMock = mocker.patch(
        "stubber.publish.merge_docstubs.frozen_candidates",
        autospec=True,
        return_value=[],
    )
    m_copy_and_merge_docstubs: MagicMock = mocker.patch("stubber.publish.merge_docstubs.copy_and_merge_docstubs", autospec=True)

    result = merge_all_docstubs(versions="1.19.1", ports=ports, boards=boards)

    # The fallback should be skipped entirely, so nothing is merged
    assert m_board_candidates.call_count == 1
    assert m_frozen_candidates.call_count == 0
    assert m_copy_and_merge_docstubs.call_count == 0
    assert not result


@pytest.mark.mocked
def test_copydocstubs_mocked(mocker, tmp_path, pytestconfig):
    """Test publish_multiple"""
    # use the test config
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.merge_docstubs.CONFIG", config)

    m_enrich_folder: MagicMock = mocker.patch("stubber.publish.merge_docstubs.enrich_folder", autospec=True, return_value=42)
    m_copytree: MagicMock = mocker.patch("stubber.publish.merge_docstubs.shutil.copytree", autospec=True)
    mocker.patch("stubber.publish.merge_docstubs.shutil.copy", autospec=True)

    # use files already in test set
    fw_path = Path(".") / "tests" / "data" / "micropython-1.18-esp32"
    docstub_path = Path(".") / "tests" / "data" / "micropython-1.18-docstubs"
    dest_path = tmp_path / "micropython-merged"
    result = copy_and_merge_docstubs(fw_path, dest_path, docstub_path)

    assert result == 42
    assert m_enrich_folder.call_count == 1
    assert m_copytree.call_count == 1
