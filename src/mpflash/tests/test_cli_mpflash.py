from pathlib import Path
from typing import List

import pytest
from click.testing import CliRunner
from mock import Mock
from pytest_mock import MockerFixture

# # module under test :
from mpflash import cli_main
from mpflash.ask_input import DownloadParams
from mpflash.mpremoteboard import MPRemoteBoard

# mark all tests
pytestmark = pytest.mark.mpflash

##########################################################################################
# --help


def test_mpflash_help():
    # check basic command line sanity check
    runner = CliRunner()
    result = runner.invoke(cli_main.cli, ["--help"])
    assert result.exit_code == 0
    expected = ["Usage:", "Options", "Commands", "download", "flash", "list"]
    for word in expected:
        assert word in result.output


##########################################################################################
# list


@pytest.mark.parametrize(
    "id, ex_code, args",
    [
        ("1", 0, ["list"]),
        ("2", 0, ["list", "--json"]),
        ("3", 0, ["list", "--no-progress"]),
        ("4", 0, ["list", "--json", "--no-progress"]),
    ],
)
def test_mpflash_list(id, ex_code, args: List[str], mocker: MockerFixture):

    m_list_mcus = mocker.patch("mpflash.cli_list.list_mcus", return_value=[], autospec=True)
    m_show_mcus = mocker.patch("mpflash.cli_list.show_mcus", return_value=None, autospec=True)
    m_print = mocker.patch("mpflash.cli_list.print", return_value=None, autospec=True)

    runner = CliRunner()
    result = runner.invoke(cli_main.cli, args)
    assert result.exit_code == ex_code

    m_list_mcus.assert_called_once()
    if "--json" in args:
        m_print.assert_called_once()
    if "--no-progress" not in args and "--json" not in args:
        m_show_mcus.assert_called_once()


##########################################################################################
# download


@pytest.mark.parametrize(
    "id, ex_code, args",
    [
        ("10", 0, ["download"]),
        ("20", 0, ["download", "--destination", "firmware"]),
        ("30", 0, ["download", "--version", "1.22.0"]),
        ("31", 0, ["download", "--version", "stable"]),
        ("32", 0, ["download", "--version", "stable", "--version", "1.22.0"]),
        ("40", 0, ["download", "--board", "ESP32_GENERIC"]),
        ("41", 0, ["download", "--board", "?"]),
        ("42", 0, ["download", "--board", "?", "--board", "ESP32_GENERIC"]),
        ("50", 0, ["download", "--destination", "firmware", "--version", "1.22.0", "--board", "ESP32_GENERIC"]),
        ("60", 0, ["download", "--no-clean"]),
        ("61", 0, ["download", "--clean"]),
        ("62", 0, ["download", "--force"]),
    ],
)
def test_mpflash_download(id, ex_code, args: List[str], mocker: MockerFixture):
    def fake_ask_missing_params(params: DownloadParams, action: str = "download") -> DownloadParams:
        return params

    m_connected_ports_boards = mocker.patch(
        "mpflash.cli_download.connected_ports_boards",
        return_value=(["esp32"], ["ESP32_GENERIC"]),
        autospec=True,
    )
    m_download = mocker.patch("mpflash.cli_download.download", return_value=None, autospec=True)
    m_ask_missing_params = mocker.patch(
        "mpflash.cli_download.ask_missing_params",
        Mock(side_effect=fake_ask_missing_params),
    )

    runner = CliRunner()
    result = runner.invoke(cli_main.cli, args)
    assert result.exit_code == ex_code
    if not "--board" in args:
        m_connected_ports_boards.assert_called_once()
    m_ask_missing_params.assert_called_once()
    m_download.assert_called_once()

    if "--clean" in args:
        assert m_download.call_args.args[5] == True
    if "--no-clean" in args:
        assert m_download.call_args.args[5] == False
    else:
        assert m_download.call_args.args[5] == True

    if "--force" in args:
        assert m_download.call_args.args[4] == True
    else:
        assert m_download.call_args.args[4] == False


##########################################################################################
# flash


@pytest.mark.parametrize(
    "id, ex_code, args",
    [
        ("10", 0, ["flash"]),
        ("20", 0, ["flash", "--version", "1.22.0"]),
        ("21", 0, ["flash", "--version", "stable"]),
        ("30", 0, ["flash", "--board", "ESP32_GENERIC"]),
        ("31", 0, ["flash", "--board", "?"]),
        ("40", 0, ["flash", "--no-bootloader"]),
        # faulty
        # ("81", -1, ["flash", "--board", "RPI_PICO", "--board", "ESP32_GENERIC"]),
        # ("82", -1, ["flash", "--version", "preview", "--version", "1.22.0"]),
    ],
)
def test_mpflash_flash(id, ex_code, args: List[str], mocker: MockerFixture):
    def fake_ask_missing_params(params: DownloadParams, action: str = "flash") -> DownloadParams:
        return params

    # fake COM99 as connected board
    fake = MPRemoteBoard("COM99")
    fake.connected = True
    fake.family = "micropython"
    fake.port = "esp32"
    fake.board = "ESP32_GENERIC"
    fake.version = "1.22.0"
    fake.cpu = "ESP32"

    m_mpr_connected = mocker.patch("mpflash.worklist.MPRemoteBoard", return_value=fake)
    m_mpr_connected = mocker.patch("mpflash.worklist.MPRemoteBoard.connected_boards", return_value=fake.serialport)

    m_connected_ports_boards = mocker.patch(
        "mpflash.cli_flash.connected_ports_boards",
        return_value=(["esp32"], ["ESP32_GENERIC"]),
        autospec=True,
    )
    m_flash_list = mocker.patch("mpflash.cli_flash.flash_list", return_value=None, autospec=True)
    m_ask_missing_params = mocker.patch(
        "mpflash.cli_flash.ask_missing_params",
        Mock(side_effect=fake_ask_missing_params),
    )

    runner = CliRunner()
    result = runner.invoke(cli_main.cli, args)

    if not "--board" in args:
        m_connected_ports_boards.assert_called_once()

    m_ask_missing_params.assert_called_once()
    m_mpr_connected.assert_called_once()
    # m_flash_list.assert_called_once()
    assert result.exit_code == ex_code


# TODO : Add more tests scenarios for flash
