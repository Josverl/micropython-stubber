import pytest

from stubber.publish.pathnames import board_folder_name

pytestmark = [pytest.mark.stubber]


def test_board_folder_name():
    fw = {
        "version": "1.23.0-preview",
        "mpy": "v6.2",
        "port": "samd",
        "board": "SEEED_WIO_TERMINAL",
        "family": "micropython",
        "build": "155",
        "arch": "armv7emsp",
        "ver": "1.23.0-preview-155",
        "cpu": "SAMD51P19A",
    }
    name = board_folder_name(fw)

    assert fw["family"] in name
    assert fw["port"] in name
    assert fw["board"] in name
    flat_v = fw["version"].replace(".", "_").replace("-", "_")
    assert flat_v in name

    # assert result == 'micropython-1.23.0-preview-samd-SEEED_WIO_TERMINAL'
