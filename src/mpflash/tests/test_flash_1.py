from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from mpflash.common import BootloaderMethod, FWInfo
from mpflash.flash import enter_bootloader, flash_list
from mpflash.flash.worklist import WorkList
from mpflash.mpremoteboard import MPRemoteBoard

pytestmark = [pytest.mark.mpflash]


@pytest.mark.parametrize("bl_method", iter(BootloaderMethod))
def test_enter_bootloader(mocker: MockerFixture, bl_method):
    # test if each of the bootloaders can be called
    # test enter_bootloader
    board = MPRemoteBoard("COM1")
    board.port = "stm32"
    m_bl_mpy = mocker.patch("mpflash.bootloader.activate.enter_bootloader_mpy", return_value=True)
    m_bl_man = mocker.patch("mpflash.bootloader.activate.enter_bootloader_manual", return_value=True)
    m_bl_tch = mocker.patch("mpflash.bootloader.activate.enter_bootloader_touch_1200bps", return_value=True)

    m_in_bl = mocker.patch("mpflash.bootloader.activate.in_bootloader", return_value=True) # type: ignore

    m_sleep = mocker.patch("mpflash.bootloader.activate.time.sleep")
    enter_bootloader(board, method=bl_method)

    all_calls = m_bl_mpy.call_count + m_bl_man.call_count + m_bl_tch.call_count
    if bl_method == BootloaderMethod.NONE:
        # Nothing called , no wait
        assert all_calls == 0
    else:
        assert all_calls == 1
        m_sleep.assert_called_once_with(2)


def test_enter_bootloader_auto(mocker: MockerFixture):
    # test if each of the bootloaders is called as retry
    board = MPRemoteBoard("COM1")
    board.port = "stm32"
    # first 2 will fail
    m_bl_tch = mocker.patch("mpflash.bootloader.activate.enter_bootloader_touch_1200bps", return_value=False)
    m_bl_mpy = mocker.patch("mpflash.bootloader.activate.enter_bootloader_mpy", return_value=False)
    m_bl_man = mocker.patch("mpflash.bootloader.activate.enter_bootloader_manual", return_value=True)

    m_in_bl = mocker.patch("mpflash.bootloader.activate.in_bootloader", return_value=True) # type: ignore

    m_sleep = mocker.patch("mpflash.bootloader.activate.time.sleep")
    enter_bootloader(board, method=BootloaderMethod.AUTO)

    # ? All retries are called
    assert m_bl_tch.call_count == 1
    assert m_bl_mpy.call_count == 1
    assert m_bl_man.call_count == 1

    m_sleep.assert_called_once_with(2)


@pytest.mark.parametrize("bootloader", [BootloaderMethod.NONE, BootloaderMethod.MPY])
@pytest.mark.parametrize("port", ["esp32", "esp8266", "rp2", "stm32", "samd"])
def test_flash_list(mocker: MockerFixture, test_fw_path: Path, bootloader, port):

    m_flash_uf2 = mocker.patch("mpflash.flash.flash_uf2")
    m_flash_stm32 = mocker.patch("mpflash.flash.flash_stm32")
    m_flash_esp = mocker.patch("mpflash.flash.flash_esp")
    m_mpr_run = mocker.patch("mpflash.bootloader.micropython.MPRemoteBoard.run_command")  # type: ignore
    m_bootloader = mocker.patch("mpflash.flash.enter_bootloader")

    board = MPRemoteBoard("COM1")
    board.port = "esp32"
    todo: WorkList = [
        (
            board,
            FWInfo(
                board="ESP32_GENERIC",
                port="esp32",
                #                "firmware": "https://micropython.org/resources/firmware/ESP32_GENERIC-20240222-v1.22.2.bin",
                preview=False,
                version="1.22.2",
                build="0",
                filename="rp2/RPI_PICO_W-v1.22.2.uf2",  # Bit of a Hack : uf2 test depend on a .uf2 file
                # "ext": ".bin",
                variant="ESP32_GENERIC",
            ),
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

    if port in ["esp32", "esp8266"]:
        return
    # bootloader is always called - but not for esp32/esp8266
    m_bootloader.assert_called_once()
