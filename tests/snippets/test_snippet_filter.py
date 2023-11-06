from pathlib import Path
from typing import Dict, List

import pytest

# Assuming the functions filter_issues and stub_ignore are in a module named 'mymodule'
from snippets.test_snippets import stub_ignore


@pytest.mark.parametrize(
    "line, version, port, board, ignore",
    [
        (
            "import espnow # stubs-ignore: version<1.21.0 or port.startswith('esp')",
            "1.21.0",
            "esp32",
            "",
            True,
        ),
        (
            "import espnow # stubs-ignore: skip port.lower().startswith('pybd')",
            "1.21.0",
            "PYBD_SF6",
            "",
            True,
        ),
        ("import espnow # stubs-ignore: version < 1.21.0", "1.20.0", "esp32", "", True),
        ("import espnow # stubs-ignore : version < 1.21.0", "1.20.0", "esp32", "", True),
        ("import espnow # stubs-ignore :version<1.21.0", "1.20.0", "esp32", "", True),
        ("import espnow # stubs-ignore:skip version < 1.21.0", "1.20.0", "esp32", "", True),
        ("import espnow # stubs-ignore : skip version < 1.21.0", "1.20.0", "esp32", "", True),
        ("import espnow # stubs-ignore :skip  version<1.21.0", "1.20.0", "esp32", "", True),
        ("version<1.21.0", "1.21.0", "esp32", "", False),
        ("invalid condition", "1.21.0", "esp32", "", False),
    ],
)
def test_stub_ignore(line, version, port, board, ignore):
    is_source = "#" in line
    assert (
        stub_ignore(
            line,
            version,
            port,
            board,
            linter="pytest",
            is_source=is_source,
        )
        == ignore
    )
