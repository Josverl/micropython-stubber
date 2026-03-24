"""Tests for complementary frozen module stub handling."""

from pathlib import Path

import pytest

from stubber.publish.stubpackage import append_new_definitions, get_top_level_names

pytestmark = [pytest.mark.stubber]

# ---------------------------------------------------------------------------
# get_top_level_names
# ---------------------------------------------------------------------------

_STUB_WITH_CLASS_AND_FUNC = """\
from typing import Any

class Pin:
    IN: int
    OUT: int
    def value(self) -> int: ...

def reset() -> None: ...

PWRON_RESET: int = 1
"""

_STUB_WITH_DUNDER = """\
__version__: str = "1.0"

class Pin:
    pass
"""


def test_get_top_level_names_basic():
    names = get_top_level_names(_STUB_WITH_CLASS_AND_FUNC)
    assert "Pin" in names
    assert "reset" in names
    assert "PWRON_RESET" in names
    # Import statements are not definitions
    assert "Any" not in names


def test_get_top_level_names_excludes_dunders():
    names = get_top_level_names(_STUB_WITH_DUNDER)
    # __version__ IS included because the filter is only in append_new_definitions
    assert "Pin" in names
    assert "__version__" in names


def test_get_top_level_names_syntax_error():
    names = get_top_level_names("class !!invalid!!")
    assert names == set()


def test_get_top_level_names_empty():
    names = get_top_level_names("")
    assert names == set()


# ---------------------------------------------------------------------------
# append_new_definitions
# ---------------------------------------------------------------------------

_TARGET_MACHINE = """\
from typing import Any

class Pin:
    IN: int
    def value(self) -> int: ...

def reset() -> None: ...
"""

_COMPLEMENT_WITH_NEW_CLASS = """\
from typing import Any

class Pin:
    IN: int
    def value(self) -> int: ...

class PCNT:
    IRQ_ZERO: int
    def __init__(self, unit: int) -> None: ...
    def value(self) -> int: ...
"""

_COMPLEMENT_ALL_KNOWN = """\
class Pin:
    pass

def reset() -> None: ...
"""


def test_append_new_definitions_adds_new_class(tmp_path: Path):
    """New class PCNT from the frozen stub should be appended to target."""
    target = tmp_path / "machine.pyi"
    target.write_text(_TARGET_MACHINE, encoding="utf-8")

    complement = tmp_path / "machine_frozen.pyi"
    complement.write_text(_COMPLEMENT_WITH_NEW_CLASS, encoding="utf-8")

    changed = append_new_definitions(target, complement)

    assert changed is True
    result = target.read_text(encoding="utf-8")
    # Original content preserved
    assert "class Pin:" in result
    assert "def reset" in result
    # New class appended
    assert "class PCNT:" in result
    assert "IRQ_ZERO" in result


def test_append_new_definitions_no_duplicates(tmp_path: Path):
    """Nothing should be appended when the frozen stub has no new definitions."""
    target = tmp_path / "machine.pyi"
    target.write_text(_TARGET_MACHINE, encoding="utf-8")

    complement = tmp_path / "machine_frozen.pyi"
    complement.write_text(_COMPLEMENT_ALL_KNOWN, encoding="utf-8")

    changed = append_new_definitions(target, complement)

    assert changed is False
    result = target.read_text(encoding="utf-8")
    # File is unchanged (besides possibly a trailing newline)
    assert result == _TARGET_MACHINE


def test_append_new_definitions_target_missing(tmp_path: Path):
    """Should handle gracefully when target file does not exist."""
    target = tmp_path / "nonexistent.pyi"
    complement = tmp_path / "machine_frozen.pyi"
    complement.write_text(_COMPLEMENT_WITH_NEW_CLASS, encoding="utf-8")

    changed = append_new_definitions(target, complement)
    assert changed is False


def test_append_new_definitions_complement_missing(tmp_path: Path):
    """Should handle gracefully when complement file does not exist."""
    target = tmp_path / "machine.pyi"
    target.write_text(_TARGET_MACHINE, encoding="utf-8")
    complement = tmp_path / "nonexistent.pyi"

    changed = append_new_definitions(target, complement)
    assert changed is False


def test_append_new_definitions_uses_test_data(tmp_path: Path):
    """Integration check using the actual frozen ESP32 machine.pyi test fixture."""
    frozen_stub = Path("tests/data/stub_merge/micropython-v1_24_1-frozen/esp32/GENERIC/machine.pyi")
    merged_stub = Path("tests/data/stub_merge/micropython-v1_24_1-rp2-RPI_PICO/machine.pyi")

    if not frozen_stub.exists() or not merged_stub.exists():
        pytest.skip("Test data not available")

    target = tmp_path / "machine.pyi"
    target.write_bytes(merged_stub.read_bytes())

    changed = append_new_definitions(target, frozen_stub)

    result = target.read_text(encoding="utf-8")
    # PCNT is in the frozen stub but not in the merged rp2 stub
    assert changed is True, "append_new_definitions should return True when new definitions were added"
    assert "class PCNT:" in result, "PCNT class should have been appended from frozen ESP32 stub"
    # Original merged stub content must be preserved
    original = merged_stub.read_text(encoding="utf-8")
    assert original in result, "Original merged stub content should be preserved intact"
    # The separator comment must be present
    assert "# Definitions below are from the frozen complementary module" in result
