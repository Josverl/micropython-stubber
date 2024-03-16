from pathlib import Path

import pytest

from mpflash.config import config
from mpflash.flash import find_firmware, local_firmwares


@pytest.mark.mpflash
def test_load(tmp_path: Path):
    # fw_folder = Path("/home/jos/projects/micropython-stubber/firmware")
    all = local_firmwares(config.firmware_folder)
    assert len(all) > 0


def test_find():
    fw_folder = Path(config.firmware_folder)
    fws = find_firmware(fw_folder=fw_folder, port="samd", board="SEEED_WIO_TERMINAL", preview=True)
    assert len(fws) > 0
    assert fws[0]["board"] == "SEEED_WIO_TERMINAL"
    assert int(fws[-1]["build"]) > 0
