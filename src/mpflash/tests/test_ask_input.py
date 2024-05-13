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
        "versions": ["?"],
        "boards": ["?"],
        "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
        "clean": True,
        "force": False,
    }
    params = DownloadParams(**input)
    mocker.patch("mpflash.ask_input.config", _config)
    m_prompt: MagicMock = mocker.patch("inquirer.prompt", autospec=True)
    _ = ask_missing_params(params)
    m_prompt.assert_not_called()


@pytest.mark.parametrize(
    "id, download, input, answers, check",
    [
        (
            "10 D -v ? -b ?",
            True,
            {
                "versions": ["?"],
                "boards": ["?"],
                "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
                "clean": True,
                "force": False,
            },
            {
                "versions": ["1.14.0"],
                "boards": ["OTHER_BOARD"],
            },
            {
                "versions": ["1.14.0"],
                "boards": ["OTHER_BOARD"],
            },
        ),
        (
            "11 D -v ? -b ? -b SEEED_WIO_TERMINAL",
            True,
            {
                "versions": ["?"],
                "boards": ["?", "SEEED_WIO_TERMINAL"],
                "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
                "clean": True,
                "force": False,
            },
            {
                "versions": ["1.14.0"],
                "boards": ["OTHER_BOARD"],
            },
            {
                "versions": ["1.14.0"],
                "boards": ["OTHER_BOARD", "SEEED_WIO_TERMINAL"],
            },
        ),
        (
            "20 D select version",
            True,
            {
                "versions": ["?"],
                "boards": ["SEEED_WIO_TERMINAL"],
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
            "21 D version string",
            True,
            {
                "versions": ["preview"],
                "boards": ["?"],
                "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
                "clean": True,
                "force": False,
            },
            {
                "boards": ["SEEED_WIO_TERMINAL"],
            },
            {"versions": ["preview"]},
        ),
        (
            "22 D -v preview -v ?",
            True,
            {
                "versions": ["preview", "?"],
                "boards": ["SEEED_WIO_TERMINAL"],
                "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
                "clean": True,
                "force": False,
            },
            {
                "versions": "1.14.0",
            },
            {"versions": ["preview", "1.14.0"]},
        ),
        (
            "30 D no boards",
            True,
            {
                "versions": ["stable"],
                "boards": [],
                "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
                "clean": True,
                "force": False,
            },
            {
                "boards": [
                    "SEEED_WIO_TERMINAL",
                    "FAKE_BOARD",
                ],
            },
            {
                # "versions": ["stable"]
            },
        ),
        # flash
        (
            "50 F -b ? -v preview",
            False,
            {
                "versions": ["preview"],
                "boards": ["?"],
                "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
                "serial": [],
                "erase": True,
                "bootloader": True,
                "cpu": "",
            },
            {
                "boards": ["SEEED_WIO_TERMINAL"],
                "serial": ["COM4"],
            },
            {},
        ),
        # Check that the port description is trimmed
        (
            "60 F -b ? -v preview",
            False,
            {
                "versions": ["preview"],
                "boards": ["?"],
                "fw_folder": Path("C:/Users/josverl/Downloads/firmware"),
                "serial": [],
                "erase": True,
                "bootloader": True,
                "cpu": "",
            },
            {
                "boards": ["SEEED_WIO_TERMINAL"],
                "serial": ["COM4 Manufacturer Description"],
            },
            {
                "serial": ["COM4"],
            },
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
    else:
        params = FlashParams(**input)

    m_prompt: Mock = mocker.patch("inquirer.prompt", return_value=answers, autospec=True)
    result = ask_missing_params(params)
    if answers:
        m_prompt.assert_called_once()

    # explicit checks
    for key in check:
        if isinstance(check[key], list):
            assert getattr(result, key), f"{key} should be in answers"
            assert sorted(getattr(result, key)) == sorted(check[key])
        else:
            assert getattr(result, key) == check[key]
    # are all answers used in the result
    for key in answers:
        if key not in check:
            if isinstance(answers[key], list):
                assert sorted(getattr(result, key)) == sorted(answers[key])
            else:
                assert getattr(result, key) == answers[key]
    # also make sure that the other attributes are not changed
    for key in input:
        if key not in answers and key not in check:
            if isinstance(input[key], list):
                assert sorted(getattr(result, key)) == sorted(input[key])
            else:
                assert getattr(result, key) == input[key]
