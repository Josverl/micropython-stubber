import sys

import pytest
from mock import MagicMock
from pytest_mock import MockerFixture

from mpflash.list import list_mcus
from mpflash.mpremoteboard import MPRemoteBoard

pytestmark = [pytest.mark.mpflash]


def mock_get_mcu_info(self: MPRemoteBoard):
    self.connected = True
    self.family = "micropython"
    self.cpu = "ESP32"
    self.version = "1.0.0"
    self.build = ""
    self.port = "esp32"
    self.description = "Generic ESP32 module with ESP32"
    self.board = "ESP32_GENERIC"


def test_list_mcus(mocker: MockerFixture):

    mocker.patch(
        "mpflash.list.MPRemoteBoard.connected_boards",
        return_value=[MagicMock(device="COM1")],
    )

    mocker.patch("mpflash.list.MPRemoteBoard.get_mcu_info", mock_get_mcu_info)
    result = list_mcus()
    assert len(result) == 1
