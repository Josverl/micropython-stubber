from pathlib import Path

import pytest
from mock import MagicMock
from pytest_mock import MockerFixture
from stubber.codemod.enrich import enrich_file, enrich_folder

# mark all tests
pytestmark = [pytest.mark.stubber, pytest.mark.codemod]


@pytest.mark.parametrize(
    "source_file, target_file, expected",
    [
        (
            Path("./tests/data/stub_merge/micropython-v1_18-docstubs/esp32.pyi"),
            Path("./tests/data/stub_merge/micropython-v1_18-esp32/esp32.pyi"),
            True,
        )
    ],
)
def test_enrich_file_with_stub(source_file: Path, target_file: Path, expected: bool):
    #    source_file = Path("./tests/data/stub_merge/micropython-v1_18-esp32/esp32.py")
    diffs = []
    try:
        diff_gen = enrich_file(source_file, target_file, diff=True, write_back=False)
        diffs = list(diff_gen)
    except FileNotFoundError:
        assert not expected, "docstub File not found but expected"

    if not expected:
        assert len(diffs) == 0, f"no change to the stub was expected but found: \n{diffs}"
    else:
        assert diffs, "change to the stub was expected but not found"


@pytest.mark.parametrize(
    "ID, source_folder, target_folder, expected_count",
    [
        (
            1,
            Path("./tests/data/stub_merge/micropython-v1_18-docstubs"),
            Path("./tests/data/stub_merge/micropython-v1_18-esp32"),
            9,
        ),
        (
            2,
            Path("./tests/data/stub_merge/micropython-v1_18-docstubs"),
            Path("./tests/data/stub_merge/micropython-v1_18-esp32/micropython.pyi"),
            1,
        ),
        (
            3,
            Path("./tests/data/stub_merge/micropython-v1_18-docstubs"),
            Path("./tests/data/stub_merge/micropython-v1_18-esp32/uplatform.pyi"),
            0,
        ),
        (
            4,
            Path("./tests/data/stub_merge/micropython-v1_18-docstubs/micropython.pyi"),
            Path("./tests/data/stub_merge/micropython-v1_18-esp32/micropython.pyi"),
            1,
        ),
        # test new stubs with multiple files / module
        (
            15,
            Path("./tests/data/stub_merge/micropython-v1_24_1-docstubs"),
            Path("./tests/data/stub_merge/micropython-v1_24_1-rp2-RPI_PICO/machine.pyi"),
            18,
        ),
        # Add more test cases if needed
    ],
)
def test_enrich_folder(
    ID,
    source_folder: Path,
    target_folder: Path,
    expected_count: int,
    mocker: MockerFixture,
):
    m_enrich_file = mocker.patch(
        "stubber.codemod.enrich.enrich_file", return_value="OK", autospec=True
    )
    m_run_black = mocker.patch(
        "stubber.codemod.enrich.run_black", return_value=None, autospec=True
    )
    count = enrich_folder(
        source_folder,
        target_folder,
        show_diff=False,
        write_back=False,
    )
    assert (
        count >= expected_count
    ), f"Expected at least {expected_count} files to be enriched but found {count}"
    m_run_black.assert_called_once()
    m_enrich_file.call_count >= expected_count
    assert m_enrich_file.call_count >= expected_count
