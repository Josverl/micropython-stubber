from pathlib import Path
from typing import List, Union

import pytest
from stubber.codemod.enrich import merge_candidates
from stubber.publish.candidates import board_candidates

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


@pytest.mark.parametrize(
    "id, source, target, count",
    [
        # Flakey test
        # (
        #     10,
        #     "tests/data/stub_merge/micropython-v1_24_1-docstubs",
        #     "tests/data/stub_merge/micropython-v1_24_1-rp2-RPI_PICO",
        #     57,
        # ),
        (
            11,
            "tests/data/stub_merge/micropython-v1_24_1-docstubs",
            "tests/data/stub_merge/micropython-v1_24_1-rp2-RPI_PICO/machine.pyi",
            18,
        ),
        (
            12,
            "tests/data/stub_merge/micropython-v1_24_1-docstubs",
            "tests/data/stub_merge/micropython-v1_24_1-rp2-RPI_PICO/umachine.pyi",
            0,
        ),
        (
            13,
            "tests/data/stub_merge/micropython-v1_24_1-docstubs",
            "tests/data/stub_merge/micropython-v1_24_1-rp2-RPI_PICO/micropython.pyi",
            1,
        ),
        # Flakey test
        # (
        #     23,
        #     "repos/micropython-stubs/micropython-reference",
        #     "tests/data/stub_merge/micropython-v1_24_1-docstubs",
        #     100,
        # ),
        (
            24,
            "repos/micropython-stubs/micropython-reference",
            "tests/data/stub_merge/micropython-v1_24_1-docstubs/machine",
            18,
        ),
        (
            25,
            "repos/micropython-stubs/micropython-reference",
            "tests/data/stub_merge/micropython-v1_24_1-docstubs/machine/__init__.pyi",
            1,
        ),
        # Add more test cases here
    ],
)
def test_merge_candidates(id, source, target, count):

    result = merge_candidates(Path(source), Path(target))
    assert len(result) == count
