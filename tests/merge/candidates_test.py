import pytest
from pathlib import Path
from typing import List, Union
from stubber.publish.candidates import board_candidates
from stubber.utils.config import CONFIG

pytestmark = [pytest.mark.stubber]


@pytest.mark.parametrize(
    "family, versions",
    [
        ("micropython", "v1.22.0"),
        ("micropython", "preview"),
        # Add more test cases here
    ],
)
def test_board_candidates(family: str, versions: Union[str, List[str]]):

    candidates = list(board_candidates(family=family, versions=versions))
    assert len(candidates) > 0
