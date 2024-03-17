from pathlib import Path
import pytest
from mpflash.flash import find_firmware, local_firmwares

pytestmark = pytest.mark.mpflash
####################


def test_load(tmp_path: Path):
    test_fw_folder = Path(__file__).parent / "data" / "firmware"
    all = local_firmwares(test_fw_folder)
    assert len(all) > 0


def test_find():
    test_fw_folder = Path(__file__).parent / "data" / "firmware"
    fws = find_firmware(fw_folder=test_fw_folder, port="samd", board="SEEED_WIO_TERMINAL", preview=True)
    assert len(fws) > 0
    assert fws[0]["board"] == "SEEED_WIO_TERMINAL"
    assert int(fws[-1]["build"]) > 0
