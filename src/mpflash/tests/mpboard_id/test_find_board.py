from pathlib import Path

import pytest

from mpflash.mpboard_id.board_id import find_board_designator

# Constants for test
TEST_BOARD_INFO_PATH = Path("test_board_info.csv")
HERE = Path(__file__).parent


# Helper function to create a board info file for testing
def create_board_info_file(path, content):
    with open(path, "w") as file:
        file.write(content)


# Test data for parametrized tests
@pytest.mark.parametrize(
    "test_id, descr, short_descr, board_info_content, expected_result",
    [
        # Happy path tests
        ("happy-1", "Board A", "A", "Board A,BA\nBoard B,BB", "BA"),
        ("happy-2", "Board B", "B", "Board A,BA\nBoard B,BB", "BB"),
        ("happy-3", "Board C", "C", "Board A,BA\nBoard C,BC", "BC"),
        # Edge cases
        ("edge-1", "Board A", "A", "Board A,BA\nBoard A with feature,BAF", "BA"),
        ("edge-2", "Board A with feature", "A", "Board A,BA\nBoard A with feature,BAF", "BAF"),
        # Error cases
        ("error-1", "Board X", "X", "Board A,BA\nBoard B,BB", None),
        ("error-2", "Board A", "A", "", None),
    ],
)
def test_find_board_designator_fake(test_id, descr, short_descr, board_info_content, expected_result, tmp_path):
    # Arrange
    board_info_file = tmp_path / "board_info.csv"
    create_board_info_file(board_info_file, board_info_content)
    # Act
    result = find_board_designator(descr, short_descr, board_info_file)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "test_id, descr, short_descr, board_info_content, expected_result",
    [
        # Happy path tests
        ("happy-1", "Arduino Nano RP2040 Connect", None, ".", "ARDUINO_NANO_RP2040_CONNECT"),
        ("happy-2", "Pimoroni Tiny 2040", None, "", "PIMORONI_TINY2040"),
        ("happy-3", "Board C", "C", "Board A,BA\nBoard C,BC", "BC"),
        # Edge cases
        ("edge-1", "Board A", "A", "Board A,BA\nBoard A with feature,BAF", "BA"),
        ("edge-2", "Board A with feature", "A", "Board A,BA\nBoard A with feature,BAF", "BAF"),
        # Error cases
        ("error-1", "Board X", "X", "Board A,BA\nBoard B,BB", None),
        ("error-2", "Board A", "A", "", None),
    ],
)
def test_find_board_designator_real(test_id, descr, short_descr, board_info_content, expected_result, tmp_path):
    # Act
    result = find_board_designator(descr, short_descr)
    # Assert
    assert result == expected_result

# Test for FileNotFoundError
def test_find_board_designator_csv_file_not_found(tmp_path):
    # Arrange
    non_existent_file = tmp_path / "non_existent.csv"

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        find_board_designator_csv("Board A", "A", non_existent_file)
