from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from mpflash.flash import enter_bootloader, flash_list
from mpflash.mpremoteboard import MPRemoteBoard
from mpflash.worklist import WorkList

pytestmark = [pytest.mark.mpflash]


def test_enter_bootloader(mocker: MockerFixture):
    # test enter_bootloader
    board = MPRemoteBoard("COM1")
    m_mpr_run = mocker.patch("mpflash.flash.MPRemoteBoard.run_command")
    m_sleep = mocker.patch("mpflash.flash.time.sleep")
    enter_bootloader(board)
    m_mpr_run.assert_called_once_with("bootloader", timeout=10)
    m_sleep.assert_called_once_with(2)


@pytest.mark.parametrize("bootloader", [False, True])
@pytest.mark.parametrize("port", ["esp32", "esp8266", "rp2", "stm32", "samd"])
def test_flash_list(mocker: MockerFixture, test_fw_path: Path, bootloader, port):
    m_flash_uf2 = mocker.patch("mpflash.flash.flash_uf2")
    m_flash_stm32 = mocker.patch("mpflash.flash.flash_stm32")
    m_flash_esp = mocker.patch("mpflash.flash.flash_esp")
    m_mpr_run = mocker.patch("mpflash.flash.MPRemoteBoard.run_command")
    m_bootloader = mocker.patch("mpflash.flash.enter_bootloader")

    board = MPRemoteBoard("COM1")
    board.port = "esp32"
    todo: WorkList = [
        (
            board,
            {
                "board": "ESP32_GENERIC",
                "port": "esp32",
                #                "firmware": "https://micropython.org/resources/firmware/ESP32_GENERIC-20240222-v1.22.2.bin",
                "preview": False,
                "version": "1.22.2",
                "build": "0",
                "filename": "rp2/RPI_PICO_W-v1.22.2.uf2",  # Bit of a Hack : uf2 test depend on a .uf2 file
                #                "ext": ".bin",
                "variant": "ESP32_GENERIC",
            },
        )
    ]

    # test flash_list
    board.port = port
    result = flash_list(todo, test_fw_path, erase=False, bootloader=bootloader)
    assert result
    assert len(result) == 1
    if port in ["esp32", "esp8266"]:
        m_flash_esp.assert_called_once()
    else:
        m_flash_esp.assert_not_called()
    if port in ("rp2", "samd", "nrf"):
        m_flash_uf2.assert_called_once()
    else:
        m_flash_uf2.assert_not_called()
    if port == "stm32":
        m_flash_stm32.assert_called_once()
    else:
        m_flash_stm32.assert_not_called()
    if bootloader and port not in ["esp32", "esp8266"]:
        # no enter bootloader on esp32
        m_bootloader.assert_called_once()
    else:
        m_bootloader.assert_not_called()
