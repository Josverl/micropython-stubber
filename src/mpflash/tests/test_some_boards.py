import pytest

from mpflash.ask_input import some_boards


@pytest.mark.parametrize(
    "answers, approx",
    [
        (
            {
                "versions": ("preview",),
                "port": "rp2",
            },
            20,
        ),
        (
            {
                "versions": ("v1.20.0",),
                "port": "rp2",
            },
            12,
        ),
        (
            {
                "versions": ("1.20.0",),
                "port": "rp2",
            },
            12,
        ),
        # should not contain v1.17 boards
        (
            {
                "versions": ("stable",),
                "port": "mimxrt",
            },
            12,
        ),
    ],
)
def test_some_boards(answers: dict, approx: int):

    # Act
    result = some_boards(answers)

    # Assert
    assert len(result) == pytest.approx(approx, abs=5)
