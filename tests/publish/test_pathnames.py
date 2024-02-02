import pytest

from stubber.publish.pathnames import board_folder_name, get_base


@pytest.mark.parametrize(
    "expected_base, candidate, version",
    [
        ("micropython-v1_22", {"family": "MicroPython", "version": "1.22"}, None),
        ("micropython-v1_22_1", {"family": "MicroPython", "version": "1.22"}, "1.22.1"),
        ("micropython-v1_22_2", {"family": "MicroPython"}, "1.22.2"),
        ("micropython-v1_23_0-preview", {"family": "MicroPython", "version": "1.23.0-preview"}, None),
    ],
)
def test_get_base_with_version(expected_base, candidate, version):
    base = get_base(candidate, version)
    assert base == expected_base


@pytest.mark.parametrize(
    "expected_folder_name, fw, version ",
    [
        (
            "micropython-v1_22_1-esp8266-ESP8266_GENERIC",
            {"family": "MicroPython", "port": "esp8266", "board": "ESP8266_GENERIC", "version": "1.22.1"},
            None,
        ),
        (
            "micropython-v1_23_4-esp8266-ESP8266_GENERIC",
            {"family": "MicroPython", "port": "esp8266", "board": "ESP8266_GENERIC", "version": "1.23.4"},
            "1.23.4",
        ),
        (
            "micropython-v1_23_5-preview-esp8266-ESP8266_GENERIC",
            {"family": "MicroPython", "port": "esp8266", "board": "ESP8266_GENERIC", "version": "1.23.5-preview"},
            "1.23.5-preview",
        ),
    ],
)
def test_board_folder_name(expected_folder_name: str, fw: dict, version: str):
    folder_name = board_folder_name(fw, version=version)
    assert folder_name == expected_folder_name
