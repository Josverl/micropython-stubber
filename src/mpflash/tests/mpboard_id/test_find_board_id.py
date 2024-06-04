from pathlib import Path

import pytest

from mpflash.errors import MPFlashError
from mpflash.mpboard_id.board_id import _find_board_id_by_description, find_board_id_by_description  # type: ignore

pytestmark = [pytest.mark.mpflash]

# Constants for test
HERE = Path(__file__).parent


@pytest.mark.parametrize(
    "test_id,version, descr, short_descr,  expected_result",
    [
        # Happy path tests
        ("happy-1", "stable", "Arduino Nano RP2040 Connect", None, "ARDUINO_NANO_RP2040_CONNECT"),
        ("happy-2", "stable", "Pimoroni Tiny 2040", None, "PIMORONI_TINY2040"),
        ("happy-3", "stable", "Pimoroni Tiny 2040", "", "PIMORONI_TINY2040"),
        ("happy-4", "stable", "Generic ESP32 module with ESP32", "Generic ESP32 module", "ESP32_GENERIC"),
        # Edge cases
        ("edge-1", "stable", "Pimoroni Tiny 2040 LONG", "Pimoroni Tiny 2040", "PIMORONI_TINY2040"),
        ("edge-2", "stable", "Generic ESP32 module with ESP32 OTA", "Generic ESP32 module with ESP32", "ESP32_GENERIC"),
        # v13.0
        ("esp32_v1.13-a", "v1.13", "ESP32 module with ESP32", None, "GENERIC"),
        ("esp32_v1.13-b", "v1.13", "ESP32 module with ESP32", "ESP32 module", "GENERIC"),
        ("esp32_v1.14-a", "v1.14", "ESP32 module with ESP32", None, "GENERIC"),
        ("esp32_v1.15-a", "v1.15", "ESP32 module with ESP32", None, "GENERIC"),
        ("esp32_v1.16-a", "v1.16", "ESP32 module with ESP32", None, "GENERIC"),
        ("esp32_v1.17-a", "v1.17", "ESP32 module with ESP32", None, "GENERIC"),
        ("esp32_v1.18-a", "v1.18", "ESP32 module with ESP32", None, "GENERIC"),
        ("esp32_v1.19.1-a", "v1.19.1", "ESP32 module with ESP32", None, "GENERIC"),
        ("esp32_v1.20.0-a", "v1.20.0", "ESP32 module with ESP32", None, "GENERIC"),
        # ESP32 board names changed in v1.21.0
        ("esp32_v1.21.0-a", "v1.21.0", "ESP32 module with ESP32", None, "UNKNOWN_BOARD"),
        ("esp32_v1.22.0-a", "v1.22.0", "ESP32 module with ESP32", None, "UNKNOWN_BOARD"),
        ("esp32_v1.21.0-a", None, "ESP32 module with ESP32", None, "GENERIC"),
        ("esp32_v1.22.0-a", None, "ESP32 module with ESP32", None, "GENERIC"),
        # PICO
        ("pico_v1.19.1-old", "v1.19.1", "Raspberry Pi Pico with RP2040", "Raspberry Pi Pico", "PICO"),
        ("pico_v1.19.1-new", "v1.19.1", "Raspberry Pi Pico with RP2040", "Raspberry Pi Pico", "RPI_PICO"),
        # Error cases
        ("error-1", "stable", "Board X", "X", None),
        ("error-2", "stable", "Board A", "A", None),
    ],
)
def test_find_board_id_real(test_id, descr, short_descr, expected_result, version):
    # Act
    if not expected_result:
        with pytest.raises(MPFlashError):
            # internal method raises exception
            _find_board_id_by_description(descr=descr, short_descr=short_descr, version=version)
    else:
        result = find_board_id_by_description(descr=descr, short_descr=short_descr, version=version)
        # Assert
        assert result == expected_result


# Test for FileNotFoundError
def test_find_board_id_file_not_found(tmp_path):
    # Arrange
    non_existent_file = tmp_path / "non_existent.csv"

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        find_board_id_by_description("Board A", "A", version="stable", board_info=non_existent_file)
