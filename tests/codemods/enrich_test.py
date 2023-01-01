from pathlib import Path

import pytest
from stubber.codemod.enrich import enrich_folder, enrich_file

# mark all tests
pytestmark = pytest.mark.codemod


@pytest.mark.parametrize(
    "source_file, expected",
    [
        (Path("./tests/data/stub_merge/micropython-v1_18-esp32/esp32.py"), True),
        (Path("./tests/data/stub_merge/micropython-v1_18-esp32/builtins.py"), False),
    ],
)
def test_enrich_file_with_stub(source_file: Path, expected: bool):
    #    source_file = Path("./tests/data/stub_merge/micropython-v1_18-esp32/esp32.py")
    diff = None
    docstub_path = Path("./tests/data/stub_merge/micropython-v1_18-docstubs")
    try:
        diff = enrich_file(source_file, docstub_path, diff=True, write_back=False)
    except FileNotFoundError:
        assert not expected, "docstub File not found but expected"

    if not expected:
        assert diff is None, f"no change to the stub was expected but found: \n{diff}"
    else:
        assert len(diff) > 0, "change to the stub was expected but not found"


def test_enrich_folder():
    count = enrich_folder(
        Path("./tests/data/stub_merge/micropython-v1_18-esp32"),
        Path("./tests/data/stub_merge/micropython-v1_18-docstubs"),
        show_diff=False,
        write_back=False,
    )
    assert count >= 18
