"""Tests for complementary frozen module stub handling."""

from pathlib import Path

import pytest

from stubber.publish.enums import StubSource
from stubber.publish.stubpackage import Builder, append_new_definitions, get_top_level_names

from .fakeconfig import FakeConfig

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


# ---------------------------------------------------------------------------
# get_top_level_names — additional branch coverage
# ---------------------------------------------------------------------------

_STUB_WITH_UNANNOTATED_ASSIGNS = """\
X = 5
Y = "hello"
"""

_STUB_WITH_COMPOUND_STATEMENT = """\
if True:
    pass
"""


def test_get_top_level_names_unannotated_assign():
    """Un-annotated top-level assignments should be collected."""
    names = get_top_level_names(_STUB_WITH_UNANNOTATED_ASSIGNS)
    assert "X" in names
    assert "Y" in names


def test_get_top_level_names_compound_statement():
    """Compound statements (if, for, while) at module level produce no names."""
    names = get_top_level_names(_STUB_WITH_COMPOUND_STATEMENT)
    assert names == set()


def test_get_top_level_names_async_function():
    """Async functions are cst.FunctionDef with .asynchronous set — should be collected."""
    names = get_top_level_names("async def async_fn() -> None: ...\n")
    assert "async_fn" in names


def test_get_top_level_names_attribute_assign_not_collected():
    """Attribute assignments (a.b = 5) are not simple Name targets — should be ignored."""
    names = get_top_level_names("a.b = 5\n")
    # 'a' or 'b' should not appear — only bare Name targets are collected
    assert "a" not in names
    assert "b" not in names
    assert names == set()


# ---------------------------------------------------------------------------
# append_new_definitions — additional branch coverage
# ---------------------------------------------------------------------------

_COMPLEMENT_WITH_ASSIGNS = """\
from typing import Any

class Pin:
    pass

NEW_CONST = 42
NEW_TYPED: int = 99
"""


def test_append_new_definitions_invalid_complement_source(tmp_path: Path):
    """Complement with invalid syntax should return False and leave target unchanged."""
    target = tmp_path / "machine.pyi"
    target.write_text("class Pin: ...\n", encoding="utf-8")

    complement = tmp_path / "bad.pyi"
    complement.write_text("class !!invalid!!\n", encoding="utf-8")

    changed = append_new_definitions(target, complement)

    assert changed is False
    assert target.read_text(encoding="utf-8") == "class Pin: ...\n"


def test_append_new_definitions_unannotated_assign(tmp_path: Path):
    """Un-annotated top-level assignment in complement should be appended."""
    target = tmp_path / "machine.pyi"
    target.write_text("class Pin: ...\n", encoding="utf-8")

    complement = tmp_path / "comp.pyi"
    complement.write_text("NEW_CONST = 42\n", encoding="utf-8")

    changed = append_new_definitions(target, complement)

    assert changed is True
    result = target.read_text(encoding="utf-8")
    assert "NEW_CONST" in result


def test_append_new_definitions_annotated_assign(tmp_path: Path):
    """Annotated top-level assignment in complement should be appended."""
    target = tmp_path / "machine.pyi"
    target.write_text("class Pin: ...\n", encoding="utf-8")

    complement = tmp_path / "comp.pyi"
    complement.write_text("NEW_TYPED: int = 99\n", encoding="utf-8")

    changed = append_new_definitions(target, complement)

    assert changed is True
    result = target.read_text(encoding="utf-8")
    assert "NEW_TYPED" in result


def test_append_new_definitions_mixed_assigns(tmp_path: Path):
    """Mix of new and existing assignments: only new ones appended, dunders skipped."""
    target = tmp_path / "mod.pyi"
    target.write_text("class Pin: ...\nEXISTING = 1\n", encoding="utf-8")

    complement = tmp_path / "comp.pyi"
    # EXISTING is in target, __dunder__ should be skipped, NEW_VAR should be appended
    complement.write_text("EXISTING = 1\n__dunder__ = 'x'\nNEW_VAR = 100\n", encoding="utf-8")

    changed = append_new_definitions(target, complement)

    assert changed is True
    result = target.read_text(encoding="utf-8")
    assert "NEW_VAR" in result
    assert "__dunder__" not in result
    assert result.count("EXISTING") == 1


def test_append_new_definitions_compound_stmt_in_complement(tmp_path: Path):
    """Compound statements (if/for/while) in complement produce no name — silently ignored."""
    target = tmp_path / "mod.pyi"
    target.write_text("class Pin: ...\n", encoding="utf-8")

    complement = tmp_path / "comp.pyi"
    complement.write_text("if True:\n    pass\n", encoding="utf-8")

    changed = append_new_definitions(target, complement)

    assert changed is False
    assert target.read_text(encoding="utf-8") == "class Pin: ...\n"


def test_append_new_definitions_attribute_assign_ignored(tmp_path: Path):
    """Attribute-target assignments (a.b = 5) in complement produce no name — silently ignored."""
    target = tmp_path / "mod.pyi"
    target.write_text("class Pin: ...\n", encoding="utf-8")

    complement = tmp_path / "comp.pyi"
    complement.write_text("a.b = 5\n", encoding="utf-8")

    changed = append_new_definitions(target, complement)

    assert changed is False


# ---------------------------------------------------------------------------
# copy_folder — complementary merge paths
# ---------------------------------------------------------------------------

_FROZEN_MACHINE_SOURCE = """\
from typing import Any

class Pin:
    IN: int
    def value(self) -> int: ...

class PCNT:
    IRQ_ZERO: int
    def __init__(self, unit: int, pin: Any) -> None: ...
    def value(self) -> int: ...
"""

_MERGED_MACHINE_SOURCE = """\
from typing import Any

class Pin:
    IN: int
    def value(self) -> int: ...

def reset() -> None: ...
"""

_TEST_MPY_VERSION = "1.24.1"
_TEST_FROZEN_SRC_ESP32 = "micropython-v1_24_1-frozen/esp32/GENERIC"
_TEST_FROZEN_SRC_STM32 = "micropython-v1_24_1-frozen/stm32/GENERIC"


def test_copy_folder_esp32_merges_into_existing_target(tmp_path, mocker):
    """copy_folder should merge PCNT from frozen esp32 machine.pyi into existing stub."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=tmp_path / "stubs",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    # Set up the frozen stub source
    frozen_dir = config.stub_path / Path(_TEST_FROZEN_SRC_ESP32)
    frozen_dir.mkdir(parents=True)
    (frozen_dir / "machine.pyi").write_text(_FROZEN_MACHINE_SOURCE, encoding="utf-8")

    # Create a Builder instance and pre-populate package_path with a merged machine.pyi
    builder = Builder("micropython-esp32-stubs", port="esp32", board="GENERIC", mpy_version=_TEST_MPY_VERSION)
    builder.package_path.mkdir(parents=True, exist_ok=True)
    target_machine = builder.package_path / "machine.pyi"
    target_machine.write_text(_MERGED_MACHINE_SOURCE, encoding="utf-8")

    builder.copy_folder(StubSource.FROZEN, Path(_TEST_FROZEN_SRC_ESP32))

    result = target_machine.read_text(encoding="utf-8")
    # Original content preserved
    assert "def reset" in result
    assert "class Pin:" in result
    # New class from frozen stub appended
    assert "class PCNT:" in result
    assert "IRQ_ZERO" in result
    assert "# Definitions below are from the frozen complementary module" in result


def test_copy_folder_esp32_copies_when_target_absent(tmp_path, mocker):
    """copy_folder should copy frozen esp32 machine.pyi as-is when no target exists yet."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=tmp_path / "stubs",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    # Set up the frozen stub source (no machine.pyi in package_path yet)
    frozen_dir = config.stub_path / Path(_TEST_FROZEN_SRC_ESP32)
    frozen_dir.mkdir(parents=True)
    (frozen_dir / "machine.pyi").write_text(_FROZEN_MACHINE_SOURCE, encoding="utf-8")

    builder = Builder("micropython-esp32-stubs", port="esp32", board="GENERIC", mpy_version=_TEST_MPY_VERSION)
    builder.package_path.mkdir(parents=True, exist_ok=True)
    # machine.pyi does NOT exist in package_path

    builder.copy_folder(StubSource.FROZEN, Path(_TEST_FROZEN_SRC_ESP32))

    target_machine = builder.package_path / "machine.pyi"
    assert target_machine.exists(), "Frozen stub should have been copied when no target was present"
    result = target_machine.read_text(encoding="utf-8")
    assert "class PCNT:" in result


def test_copy_folder_non_esp32_frozen_machine_skipped(tmp_path, mocker):
    """copy_folder should silently skip frozen machine.pyi for non-complementary ports."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=tmp_path / "stubs",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    # Set up a stm32 frozen machine.pyi (not in COMPLEMENTARY_FROZEN_MODULES)
    frozen_dir = config.stub_path / Path(_TEST_FROZEN_SRC_STM32)
    frozen_dir.mkdir(parents=True)
    (frozen_dir / "machine.pyi").write_text("class Pin: ...\n", encoding="utf-8")

    builder = Builder("micropython-stm32-stubs", port="stm32", board="GENERIC", mpy_version=_TEST_MPY_VERSION)
    builder.package_path.mkdir(parents=True, exist_ok=True)

    builder.copy_folder(StubSource.FROZEN, Path(_TEST_FROZEN_SRC_STM32))

    # machine.pyi should NOT have been copied (stm32 is not in COMPLEMENTARY_FROZEN_MODULES)
    target_machine = builder.package_path / "machine.pyi"
    assert not target_machine.exists(), "machine.pyi should be skipped for non-complementary port"


def test_copy_folder_esp32_no_new_defs_target_unchanged(tmp_path, mocker):
    """copy_folder: when target already has all frozen defs, target should remain unchanged."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=tmp_path / "stubs",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    frozen_dir = config.stub_path / Path(_TEST_FROZEN_SRC_ESP32)
    frozen_dir.mkdir(parents=True)
    # Frozen stub only has Pin — already present in the target
    (frozen_dir / "machine.pyi").write_text("class Pin: ...\n", encoding="utf-8")

    builder = Builder("micropython-esp32-stubs", port="esp32", board="GENERIC", mpy_version=_TEST_MPY_VERSION)
    builder.package_path.mkdir(parents=True, exist_ok=True)
    target_machine = builder.package_path / "machine.pyi"
    # Target already has Pin AND PCNT — nothing new in the frozen stub
    target_machine.write_text("class Pin: ...\nclass PCNT: ...\n", encoding="utf-8")
    original_content = target_machine.read_text(encoding="utf-8")

    builder.copy_folder(StubSource.FROZEN, Path(_TEST_FROZEN_SRC_ESP32))

    # Target should be unchanged because append_new_definitions returned False
    assert target_machine.read_text(encoding="utf-8") == original_content


def test_copy_folder_empty_source_dir(tmp_path, mocker):
    """copy_folder: empty source directory — no files should appear in package_path."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=tmp_path / "stubs",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    # Empty source directory (no .pyi files)
    frozen_dir = config.stub_path / Path(_TEST_FROZEN_SRC_ESP32)
    frozen_dir.mkdir(parents=True)

    builder = Builder("micropython-esp32-stubs", port="esp32", board="GENERIC", mpy_version=_TEST_MPY_VERSION)
    builder.package_path.mkdir(parents=True, exist_ok=True)

    builder.copy_folder(StubSource.FROZEN, Path(_TEST_FROZEN_SRC_ESP32))

    # No .pyi files should have been added
    assert list(builder.package_path.rglob("*.pyi")) == []


def test_copy_folder_non_frozen_filtered_stub_skipped(tmp_path, mocker):
    """copy_folder: FIRMWARE builtins.pyi is in filter but stub_type is not FROZEN — skip."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=tmp_path / "stubs",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    firmware_dir = config.stub_path / "micropython-v1_24_1-esp32"
    firmware_dir.mkdir(parents=True)
    (firmware_dir / "builtins.pyi").write_text("class int: ...\n", encoding="utf-8")

    builder = Builder("micropython-esp32-stubs", port="esp32", board="GENERIC", mpy_version=_TEST_MPY_VERSION)
    builder.package_path.mkdir(parents=True, exist_ok=True)

    builder.copy_folder(StubSource.FIRMWARE, Path("micropython-v1_24_1-esp32"))

    # builtins.pyi is in STUBS_COPY_FILTER[FIRMWARE] → should be skipped
    assert not (builder.package_path / "builtins.pyi").exists()


def test_copy_folder_unfiltered_file_is_copied(tmp_path, mocker):
    """copy_folder: a file not in any filter should be copied to package_path."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=tmp_path / "stubs",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    firmware_dir = config.stub_path / "micropython-v1_24_1-esp32"
    firmware_dir.mkdir(parents=True)
    # esp32.pyi is not in any STUBS_COPY_FILTER
    (firmware_dir / "esp32.pyi").write_text("class NVS: ...\n", encoding="utf-8")

    builder = Builder("micropython-esp32-stubs", port="esp32", board="GENERIC", mpy_version=_TEST_MPY_VERSION)
    builder.package_path.mkdir(parents=True, exist_ok=True)

    builder.copy_folder(StubSource.FIRMWARE, Path("micropython-v1_24_1-esp32"))

    # esp32.pyi is not filtered → should be copied
    assert (builder.package_path / "esp32.pyi").exists()
    assert (builder.package_path / "esp32.pyi").read_text(encoding="utf-8") == "class NVS: ...\n"


def test_copy_folder_skips_directory_with_pyi_extension(tmp_path, mocker):
    """copy_folder: if rglob matches a directory named '*.pyi', it should be skipped (is_file check)."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=tmp_path / "stubs",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    src_dir = config.stub_path / "micropython-v1_24_1-esp32"
    src_dir.mkdir(parents=True)
    # Create a *directory* whose name ends in .pyi — unusual but covers the is_file branch
    pyi_dir = src_dir / "foo.pyi"
    pyi_dir.mkdir()

    builder = Builder("micropython-esp32-stubs", port="esp32", board="GENERIC", mpy_version=_TEST_MPY_VERSION)
    builder.package_path.mkdir(parents=True, exist_ok=True)

    builder.copy_folder(StubSource.FIRMWARE, Path("micropython-v1_24_1-esp32"))

    # The directory should NOT have been copied to package_path
    assert not (builder.package_path / "foo.pyi").exists()


