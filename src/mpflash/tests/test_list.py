import sys
from typing import List

import jsons
import pytest
import rich
import rich.measure
from mock import MagicMock
from pytest_mock import MockerFixture

import mpflash.list
from mpflash.list import list_mcus, mcu_table
from mpflash.mpremoteboard import MPRemoteBoard

pytestmark = [pytest.mark.mpflash]


# Accessibly
# make sure that the tables can be displayed on a 80 char terminal

mcus_2_txt = """
[
    {   
        "arch": "", "board": "UNKNOWN_BOARD", "build": "", "connected": true, "cpu": "nRF52840", "description": "nice!nano with nRF52840", 
        "family": "circuitpython", "firmware": {}, "mpy": "v5.2", "path": null, "port": "nRF52840", "serialport": "COM27", "version": "8.2.10"
    }, 
    {
        "arch": "armv7emsp", "board": "SEEED_WIO_TERMINAL", "build": "341", "connected": true, "cpu": "SAMD51P19A", "description": "Wio Terminal D51R with SAMD51P19A", 
        "family": "micropython", "firmware": {}, "mpy": "v6.3", "path": null, "port": "samd", "serialport": "COM8", "version": "1.23.0-preview"
    }
]
"""
mcus_2 = jsons.loads(mcus_2_txt, List[MPRemoteBoard])


@pytest.mark.parametrize(
    "term_width, mcus",
    [
        (110, mcus_2),
        (80, mcus_2),
        (50, mcus_2),
    ],
)
@pytest.mark.parametrize("has_build", [True, False])
def test_mcu_table_width(term_width: int, mcus, has_build: bool):
    if not has_build:
        for mcu in mcus:
            mcu.build = ""
    mpflash.list.console = rich.console.Console(file=sys.stdout, width=term_width)
    table = mcu_table(mcus, title="Connected boards", refresh=False)
    measurement = rich.measure.measure_renderables(mpflash.list.console, mpflash.list.console.options, [table])
    # make sure the minimum width is less than the terminal width
    assert measurement.minimum <= term_width
    # last column should be the build column if any of the mcus have a build
    assert has_build == (table.columns[-1].header in ("Build", "Bld"))


# def mock_get_mcu_info(self: MPRemoteBoard):
#     self.connected = True
#     self.family = "micropython"
#     self.cpu = "ESP32"
#     self.version = "1.0.0"
#     self.build = ""
#     self.port = "esp32"
#     self.description = "Generic ESP32 module with ESP32"
#     self.board = "ESP32_GENERIC"


# def test_list_mcus(mocker: MockerFixture):

#     mocker.patch(
#         "mpflash.list.MPRemoteBoard.connected_boards",
#         return_value=[MagicMock(device="COM1")],
#     )

#     mocker.patch("mpflash.list.MPRemoteBoard.get_mcu_info", mock_get_mcu_info)
#     result = list_mcus(include=["*"], ignore=["COM2"], bluetooth=False)
#     assert len(result) == 1
