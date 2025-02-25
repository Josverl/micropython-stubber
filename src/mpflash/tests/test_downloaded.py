

import pytest
from pytest_mock import MockerFixture

from mpflash.common import FWInfo
from mpflash.config import config
from mpflash.downloaded import (downloaded_firmwares, filter_downloaded_fwlist,
                                find_downloaded_firmware)

pytestmark = [pytest.mark.mpflash]


def test_downloaded_firmwares(mocker: MockerFixture, test_fw_path):
    firmwares = downloaded_firmwares(test_fw_path)
    assert firmwares
    assert all(f.filename for f in firmwares)


#########################################################################
# minimal Local test setup # TODO: Add to CI
# mpflash download --version 1.19.1 --board PICO
# mpflash download --version 1.22.2 --board RPI_PICO
# mpflash download --version 1.22.2 --board RPI_PICO_W
# mpflash download --version preview --board ESP32_GENRIC
#########################################################################

@pytest.mark.parametrize(
    "port, board_id, version, OK",
    [
        ("esp32", "ESP32_GENERIC", "preview", True),
        ("esp32", "GENERIC", "preview", True),
        # Old and new names for PICO
        ("rp2", "RPI_PICO", "1.22.2", True),
        ("rp2", "PICO", "1.22.2", True),
        # old name for PICO
        ("rp2", "PICO", "1.19.1", True),
        # old and new name for PICO_W
        ("rp2", "RPI_PICO_W", "1.22.2", True),
        ("rp2", "PICO_W", "1.22.2", True),
        ("fake", "NO_BOARD", "1.22.2", False),
        # test for board_id = board.replace("_", "-")
    ],
)
@pytest.mark.parametrize("actual", [False])  # Add True if you want to test agains the actual downloads
@pytest.mark.parametrize("variants", [False, True])  #
def test_find_downloaded_firmware(port, board_id, version, OK, test_fw_path, actual: bool, variants: bool):
    if actual:
        fw_path = config.firmware_folder
        if not fw_path.exists():
            pytest.xfail("This test may not work in CI, as the firmware may not be downloaded.")
    else:
        fw_path = test_fw_path
    result = find_downloaded_firmware(
        version=version,
        board_id=board_id,
        port=port,
        variants=variants,
        fw_folder=fw_path,
        trie=1,
    )
    if not OK:
        assert not result
        return

    assert result
    assert all(isinstance(fw, FWInfo) for fw in result), "All elements should be FWInfo objects"
    assert all(fw.port == port for fw in result)
    # same board ; or PORT_board
    assert all(fw.board in (board_id, f"{port.upper()}_{board_id}", f"RPI_{board_id}") for fw in result)

    if version == "preview":
        assert all( fw.preview for fw in result)
    else:
        assert all(version in fw.version for fw in result) 
    assert all(version in fw.filename for fw in result)
    if not variants:
        # variante ==  board or PORT_board
        assert all(fw.variant in (board_id, f"{port.upper()}_{board_id}", f"RPI_{board_id}") for fw in result)


@pytest.mark.parametrize(
    "port, board_id, version, OK",
    [
        ("esp32", "ESP32_GENERIC", "preview", True),
        ("rp2", "RPI_PICO", "1.22.2", True),
        ("rp2", "RPI_PICO_W", "1.22.2", True),
        ("rp2", "PICO_W", "1.22.2", False),  # name change
        ("rp2", "PICO", "1.22.2", False),  # name change
        ("esp32", "GENERIC", "preview", False),  # name change
        # ("fake", "NO_BOARD", "1.22.2", False),
        # test for board_id = board.replace("_", "-")
    ],
)
@pytest.mark.parametrize("actual", [False])  # , True still fails in CI
def test_filter_downloaded_fwlist(port, board_id, version, OK, test_fw_path, actual: bool):
    if actual:
        fw_path = config.firmware_folder
        if not fw_path.exists():
            pytest.xfail("This test may not work in CI, as the firmware may/will not be downloaded.")
    else:
        fw_path = test_fw_path
    fw_list = downloaded_firmwares(fw_path)

    fwlist = filter_downloaded_fwlist(
        fw_list=fw_list,
        board_id=board_id,
        version=version,
        port=port,
        variants=False,
        selector={},
    )
    if not OK:
        assert not fwlist
        return
    assert fwlist
