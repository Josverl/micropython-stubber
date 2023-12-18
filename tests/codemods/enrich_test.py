from pathlib import Path

import pytest
from mock import MagicMock
from pytest_mock import MockerFixture

from stubber.codemod.enrich import enrich_file, enrich_folder

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

    if expected == False:
        assert diff is None, "no change to the stub was expected but found: \n{}".format(diff)
    else:
        assert len(diff) > 0, "change to the stub was expected but not found"


@pytest.mark.parametrize(
    "source_folder, docstub_folder, expected_count",
    [
        (
            Path("./tests/data/stub_merge/micropython-v1_18-esp32"),
            Path("./tests/data/stub_merge/micropython-v1_18-docstubs"),
            22,
        ),
        (
            Path("./tests/data/stub_merge/micropython-v1_18-esp32/micropython.pyi"),
            Path("./tests/data/stub_merge/micropython-v1_18-docstubs"),
            1,
        ),
        (
            Path("./tests/data/stub_merge/micropython-v1_18-esp32/uplatform.pyi"),
            Path("./tests/data/stub_merge/micropython-v1_18-docstubs"),
            1,
        ),
        (
            Path("./tests/data/stub_merge/micropython-v1_18-esp32/micropython.pyi"),
            Path("./tests/data/stub_merge/micropython-v1_18-docstubs/micropython.pyi"),
            1,
        ),
        # Add more test cases if needed
    ],
)
def test_enrich_folder(
    source_folder: Path, docstub_folder: Path, expected_count: int, mocker: MockerFixture
):
    m_enrich_file = mocker.patch(
        "stubber.codemod.enrich.enrich_file", return_value="OK", autospec=True
    )
    m_run_black = mocker.patch(
        "stubber.codemod.enrich.run_black", return_value=None, autospec=True
    )
    count = enrich_folder(
        source_folder,
        docstub_folder,
        show_diff=False,
        write_back=False,
    )
    assert (
        count >= expected_count
    ), f"Expected at least {expected_count} files to be enriched but found {count}"
    m_run_black.assert_called_once()
    m_enrich_file.assert_called()
    assert m_enrich_file.call_count >= count
