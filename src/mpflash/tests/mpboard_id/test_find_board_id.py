from pathlib import Path

import pytest

from mpflash.errors import MPFlashError
from mpflash.mpboard_id.board_id import find_board_id

pytestmark = [pytest.mark.mpflash]

# Constants for test
HERE = Path(__file__).parent


@pytest.mark.parametrize(
    "test_id, descr, short_descr,  expected_result",
    [
        # Happy path tests
        ("happy-1", "Arduino Nano RP2040 Connect", None, "ARDUINO_NANO_RP2040_CONNECT"),
        ("happy-2", "Pimoroni Tiny 2040", None, "PIMORONI_TINY2040"),
        ("happy-3", "Pimoroni Tiny 2040", "", "PIMORONI_TINY2040"),
        ("happy-4", "Generic ESP32 module with ESP32", "Generic ESP32 module", "ESP32_GENERIC"),
        # Edge cases
        ("edge-1", "Pimoroni Tiny 2040 LONG", "Pimoroni Tiny 2040", "PIMORONI_TINY2040"),
        ("edge-2", "Generic ESP32 module with ESP32 OTA", "Generic ESP32 module with ESP32", "ESP32_GENERIC"),
        # Error cases
        ("error-1", "Board X", "X", None),
        ("error-2", "Board A", "A", None),
    ],
)
def test_find_board_id_real(test_id, descr, short_descr, expected_result):
    # Act
    if not expected_result:
        with pytest.raises(MPFlashError):
            find_board_id(descr, short_descr)
    else:
        result = find_board_id(descr, short_descr)
        # Assert
        assert result == expected_result


# Test for FileNotFoundError
def test_find_board_id_file_not_found(tmp_path):
    # Arrange
    non_existent_file = tmp_path / "non_existent.csv"

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        find_board_id("Board A", "A", non_existent_file)
