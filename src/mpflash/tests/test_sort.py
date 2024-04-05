from pathlib import Path

import pytest

from mpflash.flash import find_firmware, local_firmwares

pytestmark = [pytest.mark.mpflash]
####################
# NOTE: this test has a conflict with tests in the stubber that load a mock of the ujson module
# this is due to the fact that the jsonlines module tries to use ujson as a backend if it is available


def test_load(tmp_path: Path):
    test_fw_folder = Path(__file__).parent / "data" / "firmware"
    all = local_firmwares(test_fw_folder)
    assert len(all) > 0


def test_find():
    test_fw_folder = Path(__file__).parent / "data" / "firmware"
    fws = find_firmware(fw_folder=test_fw_folder, port="samd", board="SEEED_WIO_TERMINAL",version="preview")
    assert len(fws) > 0
    assert fws[0]["board"] == "SEEED_WIO_TERMINAL"
    assert int(fws[-1]["build"]) > 0
