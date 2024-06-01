from pathlib import Path

import pytest

from mpflash.downloaded import downloaded_firmwares, find_downloaded_firmware

pytestmark = [pytest.mark.mpflash]
####################
# NOTE: this test has a conflict with tests in the stubber that load a mock of the ujson module
# this is due to the fact that the jsonlines module tries to use ujson as a backend if it is available


def test_load(tmp_path: Path, test_fw_path: Path):
    all = downloaded_firmwares(test_fw_path)
    assert len(all) > 0


def test_find(test_fw_path: Path):
    fws = find_downloaded_firmware(
        fw_folder=test_fw_path, port="samd", board_id="SEEED_WIO_TERMINAL", version="preview"
    )
    assert len(fws) > 0
    assert fws[0].board == "SEEED_WIO_TERMINAL"
    assert int(fws[-1].build) > 0
