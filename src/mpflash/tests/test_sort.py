import pytest
from pathlib import Path
import mp_downloader.flasher as flasher


# def test_load():
#     fw_folder = Path("/home/jos/projects/micropython-stubber/firmware")
#     all = flasher.load_firmwares(fw_folder)
#     assert len(all) > 0


# def test_find():
#     fw_folder = Path("/home/jos/projects/micropython-stubber/firmware")
#     fws = flasher.find_firmware(fw_folder=fw_folder, port="samd", board="SEEED_WIO_TERMINAL",preview=True)
#     assert len(fws) > 0
#     assert fws[0]["board"] == "SEEED_WIO_TERMINAL"
#     assert int(fws[-1]["build"]) == 155
