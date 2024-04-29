import sys

import pytest
import requests
from mock import MagicMock, Mock
from pytest_mock import MockerFixture

from mpflash.download import board_firmware_urls, get_board_urls, get_page

pytestmark = [pytest.mark.mpflash]


def test_get_page(mocker: MockerFixture):
    page = get_page("https://micropython.org/download/esp32/")
    assert page
    assert "esp32" in page


def test_get_board_urls(mocker: MockerFixture):

    urls = get_board_urls("https://micropython.org/download/")
    assert urls

    for url in urls:
        assert url["url"].startswith("https://micropython.org/download/")
        assert url["board"]


def test_board_firmware_urls(mocker: MockerFixture):
    urls = board_firmware_urls(
        "https://micropython.org/download/esp32/",
        "esp32",
        "bin",
    )
    assert urls

    for url in urls:
        assert url.startswith("/resources/firmware")
        assert "esp32".upper() in url.upper()
        assert url.endswith("bin")
