from pathlib import Path

import pytest
from mock import MagicMock, Mock
from pytest_mock import MockerFixture

from mpflash.ask_input import DownloadParams, FlashParams, ask_missing_params

pytestmark = [pytest.mark.mpflash]


def test_ask_missing_params_no_interactivity(mocker: MockerFixture):
    # Make sure that the prompt is not called when interactive is False
    from mpflash.config import MPtoolConfig

    _config = MPtoolConfig()
    _config.interactive = False

    input = {
        "versions": ("?"),
        "boards": ("?"),
        "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
        "clean": True,
        "force": False,
    }
    params = DownloadParams(**input)
    mocker.patch("mpflash.ask_input.config", _config)
    m_prompt: MagicMock = mocker.patch("inquirer.prompt", autospec=True)
    _ = ask_missing_params(params, action="download")
    m_prompt.assert_not_called()


@pytest.mark.parametrize(
    "id, download, input, answers, check",
    [
        (
            "D ? preview",
            True,
            {
                "versions": ("preview",),
                "boards": ("?", "SEEED_WIO_TERMINAL"),
                "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
                "clean": True,
                "force": False,
            },
            {
                "versions": ["1.14.0"],
                "boards": ["SEEED_WIO_TERMINAL"],
            },
            {"versions": ["1.14.0"]},
        ),
        (
            "D select version",
            True,
            {
                "versions": ("?",),
                "boards": ("SEEED_WIO_TERMINAL"),
                "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
                "clean": True,
                "force": False,
            },
            {
                "versions": ["1.22.0"],
            },
            {"versions": ["1.22.0"]},
        ),
        # versions as string
        (
            "D version string",
            True,
            {
                "versions": ("preview",),
                "boards": ("?", "SEEED_WIO_TERMINAL"),
                "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
                "clean": True,
                "force": False,
            },
            {
                "versions": "1.14.0",
                "boards": ["SEEED_WIO_TERMINAL"],
            },
            {"versions": ["1.14.0"]},
        ),
        (
            "D no boards",
            True,
            {
                "versions": ("stable",),
                "boards": (),
                "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
                "clean": True,
                "force": False,
            },
            {
                "boards": ["FAKE_BOARD", "SEEED_WIO_TERMINAL"],
            },
            {
                # "versions": ["stable"]
            },
        ),
        # flash
        (
            "F ? preview",
            False,
            {
                "versions": ("preview",),
                "boards": ("?"),
                "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
                "serial": "",
                "erase": True,
                "bootloader": True,
                "cpu": "",
            },
            {
                "versions": ["1.14.0"],
                "boards": ["SEEED_WIO_TERMINAL"],
                "serial": "COM4",
            },
            {},
        ),
    ],
)
def test_ask_missing_params_with_interactivity(
    id: str,
    download: bool,
    input: dict,
    answers: dict,
    check: dict,
    mocker: MockerFixture,
):
    if download:
        params = DownloadParams(**input)
        action = "download"
    else:
        params = FlashParams(**input)
        action = "flash"

    m_prompt: Mock = mocker.patch("inquirer.prompt", return_value=answers, autospec=True)
    result = ask_missing_params(params, action)
    m_prompt.assert_called_once()

    # explicit checks
    for key in check:
        assert getattr(result, key) == check[key]
    # are all answers used in the result
    for key in answers:
        if key not in check:
            assert getattr(result, key) == answers[key]
    # also make sure that the other attributes are not changed
    for key in input:
        if key not in answers and key not in check:
            assert getattr(result, key) == input[key]
