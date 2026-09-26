import pytest

from stubber.codemod.enrich import enrich_file, enrich_folder, package_from_path, source_target_candidates, upackage_equal
from stubber.modcat import CP_REFERENCE_TO_DOCSTUB
from stubber.utils import cache as cache_cfg


def test_package_from_path(tmp_path):
    # Create temporary files and directories for testing
    target = tmp_path / "target.pyi"
    target.touch()
    source = tmp_path / "source.pyi"
    source.touch()
    package_name = package_from_path(target, source)
    assert package_name == "target"


@pytest.mark.parametrize(
    "id, src_pkg, dst_pkg, exp_match, exp_len",
    [
        (10, "module", "umodule", True, 6),
        (11, "umodule", "module", False, 0),
        (12, "umodule", "umodule", True, 7),
        #
        (20, "module1", "module2", False, 0),
        #
        (30, "_module", "module", True, 6),
        (31, "_module", "_module", True, 7),
        (32, "module", "_module", True, 6),
        #
        (40, "module.__init__", "module", True, 6),
        (41, "module.__init__", "module.__init__", True, 15),
        (42, "module.", "module.__init__", True, 6),
        #
        (50, "module.FOO", "module", True, 6),
        (51, "module", "module.FOO", True, 6),
        (52, "module.FOO", "module.__init__", True, 6),
        (53, "module.FOO", "module.FOO", True, 10),
        (54, "module.FOO", "module.BAR", False, 0),
    ],
)
def test_upackage_equal(id, src_pkg, dst_pkg, exp_match, exp_len):
    match, length = upackage_equal(src_pkg, dst_pkg)
    assert match == exp_match
    assert length == exp_len, f"Expected length {exp_len} but got {length}"


# Source --> target
@pytest.mark.parametrize(
    "test_id, source_files, target_files, expected_matches",
    [
        (10, ["module.pyi"], ["module.pyi"], 1),
        (11, ["module/__init__.pyi"], ["module.pyi"], 1),
        (12, ["module/__init__.pyi", "module/FOO.pyi"], ["module.pyi"], 2),
        (13, ["module/__init__.pyi", "umodule/FOO.pyi"], ["module.pyi"], 1),  # umodule is no match
        (14, ["module/__init__.pyi", "_module/FOO.pyi"], ["module.pyi"], 1),  # _module is no match
        (15, ["module/__init__.pyi", "module/bar/FOO.pyi"], ["module.pyi"], 2),
        (16, ["module/__init__.pyi", "module/FOO.pyi"], ["module/__init__.pyi"], 2),
        (
            17.1,
            ["module/__init__.pyi", "module/FOO.pyi", "module/BAR.pyi"],
            ["module/__init__.pyi"],
            3,  # Should be 3 , but there is only 1
        ),
        (
            17.2,
            ["module/__init__.pyi", "module/FOO.pyi", "module/BAZ/BAR.pyi"],
            ["module/__init__.pyi"],
            3,  # Should be 3 , but there is only 1
        ),
        (
            17.3,
            ["module/__init__.pyi", "module/FOO.pyi", "module/BAZ/BAR.pyi"],
            ["module.pyi"],
            3,  # Should be 3 , but there is only 1
        ),
        (
            18,
            ["module/__init__.pyi", "module/FOO.pyi"],
            ["module/__init__.pyi", "module/FOO.pyi"],
            2,
        ),
        (
            19,
            ["module/__init__.pyi", "module/FOO.pyi"],
            ["module/__init__.pyi", "module/FOO.pyi"],
            2,
        ),
        #
        (20, ["module1.pyi"], ["module2.pyi"], 0),
        (30, ["_module.pyi"], ["module.pyi"], 1),
        (40, ["umodule.pyi"], ["module.pyi"], 0),  ## do not merge from u_module to module
        (41, ["module.pyi"], ["umodule.pyi"], 1),  ## do  merge from module to umodule
        (50, ["module1.pyi", "module2.pyi"], ["module1.pyi", "module2.pyi"], 2),
        (60, ["module1.pyi", "module2.pyi"], ["module2.pyi", "module3.pyi"], 1),
    ],
)
def test_target_source_candidates(tmp_path, test_id, target_files, source_files, expected_matches: int):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    for source_name in source_files:
        source_file = source_dir / source_name
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.touch()
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    for target_name in target_files:
        target_file = target_dir / target_name
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.touch()
    candidates = list(source_target_candidates(source_dir, target_dir))
    assert len(candidates) == expected_matches, f"Expected {expected_matches} matches, got {len(candidates)}"


def test_package_source_prefers_exact_target_over_private_alias(tmp_path):
    source_file = tmp_path / "source" / "espnow" / "__init__.pyi"
    source_file.parent.mkdir(parents=True)
    source_file.touch()
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "_espnow.pyi").touch()
    (target_dir / "espnow.pyi").touch()

    candidates = list(source_target_candidates(source_file.parent.parent, target_dir))

    assert [candidate.target.name for candidate in candidates] == ["espnow.pyi"]


def test_aioespnow_reference_is_copied_to_docstubs():
    assert "aioespnow" in CP_REFERENCE_TO_DOCSTUB


def test_enrich_replaces_inspect_placeholder_params(tmp_path):
    source_file = tmp_path / "source.pyi"
    source_file.write_text(
        "class ESPNow:\n    def recv(self, timeout_ms: int | None = None) -> tuple[bytes | None, bytes | None]: ...\n",
        encoding="utf-8",
    )
    target_file = tmp_path / "target.pyi"
    target_file.write_text(
        "class ESPNow:\n    def recv(self, x1) -> Incomplete: ...\n",
        encoding="utf-8",
    )

    list(enrich_file(source_file, target_file, write_back=True, copy_params=False))

    assert "def recv(self, timeout_ms: int | None = None)" in target_file.read_text(encoding="utf-8")


def test_enrich_removes_method_decorator_from_module_function(tmp_path):
    source_file = tmp_path / "source.pyi"
    source_file.write_text("async def py_import(*args: str) -> tuple[Any, ...]: ...\n", encoding="utf-8")
    target_file = tmp_path / "target.pyi"
    target_file.write_text("@classmethod\ndef py_import(*args, **kwargs) -> Incomplete: ...\n", encoding="utf-8")

    list(enrich_file(source_file, target_file, write_back=True, copy_params=False))

    merged = target_file.read_text(encoding="utf-8")
    assert "@classmethod" not in merged
    assert "async def py_import(*args: str) -> tuple[Any, ...]" in merged


def test_enrich_does_not_demote_async_firmware_function(tmp_path):
    source_file = tmp_path / "source.pyi"
    source_file.write_text("def fetch(url: str) -> Response: ...\n", encoding="utf-8")
    target_file = tmp_path / "target.pyi"
    target_file.write_text("async def fetch(x1) -> Incomplete: ...\n", encoding="utf-8")

    list(enrich_file(source_file, target_file, write_back=True, copy_params=False))

    assert "async def fetch(url: str) -> Response" in target_file.read_text(encoding="utf-8")


def test_enrich_folder_removes_inherited_placeholder_across_target_files(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "parent.pyi").write_text(
        "from typing import overload\n\n"
        "class Parent:\n"
        "    def read(self, nbytes: int, /) -> bytes: ...\n"
        "    def write(self, data: bytes, timeout: int, /) -> int: ...\n"
        "    def configured(self) -> bool: ...\n"
        "    def status(self) -> int: ...\n"
        "    @overload\n"
        "    def convert(self, value: int, /) -> bytes: ...\n"
        "    @overload\n"
        "    def convert(self, value: str, /) -> str: ...\n",
        encoding="utf-8",
    )
    (source_dir / "child.pyi").write_text(
        "from parent import Parent\n\n"
        "class Child(Parent):\n"
        "    def status(self, verbose: bool = False) -> str: ...\n"
        "    def __init__(self, pin: int, /) -> None: ...\n",
        encoding="utf-8",
    )

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "parent.pyi").write_text(
        "from _typeshed import Incomplete\n\n"
        "class Parent:\n"
        "    def read(self, *args, **kwargs) -> Incomplete: ...\n"
        "    def write(self, *args, **kwargs) -> Incomplete: ...\n"
        "    def configured(self, *args, **kwargs) -> Incomplete: ...\n"
        "    def status(self, *args, **kwargs) -> Incomplete: ...\n"
        "    def convert(self, *args, **kwargs) -> Incomplete: ...\n",
        encoding="utf-8",
    )
    child_target = target_dir / "child.pyi"
    child_target.write_text(
        "from _typeshed import Incomplete\n\n"
        "class Child:\n"
        "    def read(self, *args, **kwargs) -> Incomplete: ...\n"
        "    # inspect: arity=2\n"
        "    def write(self, *args, **kwargs) -> Incomplete: ...\n"
        "    @classmethod\n"
        "    def configured(cls, *args, **kwargs) -> Incomplete: ...\n"
        "    def status(self, *args, **kwargs) -> Incomplete: ...\n"
        "    def convert(self, *args, **kwargs) -> Incomplete: ...\n"
        "    def __init__(self, pin) -> None: ...\n",
        encoding="utf-8",
    )

    enrich_folder(source_dir, target_dir, write_back=True, copy_params=True)

    merged = child_target.read_text(encoding="utf-8")
    assert "class Child(Parent):" in merged
    assert "def read" not in merged
    assert "def convert" not in merged
    assert "def write(self, *args, **kwargs) -> Incomplete" in merged
    assert "def configured(cls, *args, **kwargs) -> Incomplete" in merged
    assert "def status(self, verbose: bool = False) -> str" in merged
    assert "def __init__(self, pin: int, /) -> None" in merged


def test_enrich_folder_removes_inherited_placeholder_across_split_source_files(tmp_path):
    source_package = tmp_path / "source" / "module"
    source_package.mkdir(parents=True)
    (source_package / "__init__.pyi").touch()
    (source_package / "Parent.pyi").write_text(
        "class Parent:\n    def read(self, nbytes: int, /) -> bytes: ...\n",
        encoding="utf-8",
    )
    (source_package / "Child.pyi").write_text(
        "from .Parent import Parent\n\nclass Child(Parent):\n    def __init__(self, pin: int, /) -> None: ...\n",
        encoding="utf-8",
    )

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    target = target_dir / "module.pyi"
    target.write_text(
        "from _typeshed import Incomplete\n\n"
        "class Parent:\n"
        "    def read(self, *args, **kwargs) -> Incomplete: ...\n\n"
        "class Child:\n"
        "    def read(self, *args, **kwargs) -> Incomplete: ...\n"
        "    def __init__(self, pin) -> None: ...\n",
        encoding="utf-8",
    )

    enrich_folder(source_package.parent, target_dir, write_back=True, copy_params=True)

    merged = target.read_text(encoding="utf-8")
    assert "class Child(Parent):" in merged
    assert merged.count("def read") == 1
    assert "def read(self, nbytes: int, /) -> bytes" in merged


def test_enrich_folder_qualifies_same_named_parents_by_module(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "alpha.pyi").write_text(
        "class Base:\n    def lookup(self, key: str, /) -> bytes: ...\n",
        encoding="utf-8",
    )
    (source_dir / "beta.pyi").write_text(
        "class Base:\n    def lookup(self, key: str, default: int, /) -> int: ...\n",
        encoding="utf-8",
    )
    (source_dir / "child_a.pyi").write_text(
        "from alpha import Base as AlphaBase\n\nclass ChildA(AlphaBase): ...\n",
        encoding="utf-8",
    )
    (source_dir / "child_b.pyi").write_text(
        "import beta as beta_module\n\nclass ChildB(beta_module.Base): ...\n",
        encoding="utf-8",
    )

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "alpha.pyi").write_text("class Base: ...\n", encoding="utf-8")
    (target_dir / "beta.pyi").write_text("class Base: ...\n", encoding="utf-8")
    child_a_target = target_dir / "child_a.pyi"
    child_b_target = target_dir / "child_b.pyi"
    child_stub = (
        "from _typeshed import Incomplete\n\n"
        "class {name}:\n"
        "    # inspect: arity=2\n"
        "    def lookup(self, *args, **kwargs) -> Incomplete: ...\n"
    )
    child_a_target.write_text(child_stub.format(name="ChildA"), encoding="utf-8")
    child_b_target.write_text(child_stub.format(name="ChildB"), encoding="utf-8")

    enrich_folder(source_dir, target_dir, write_back=True, copy_params=True)

    assert "class ChildA(AlphaBase): ..." in child_a_target.read_text(encoding="utf-8")
    child_b_merged = child_b_target.read_text(encoding="utf-8")
    assert "class ChildB(beta_module.Base):" in child_b_merged
    assert "def lookup(self, *args, **kwargs) -> Incomplete" in child_b_merged


def test_enrich_folder_keeps_placeholder_for_ambiguous_or_unresolved_parent(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "parent.pyi").write_text(
        "class Parent:\n    def read(self, nbytes: int, /) -> bytes: ...\n",
        encoding="utf-8",
    )
    (source_dir / "mixin.pyi").write_text("class Mixin: ...\n", encoding="utf-8")
    (source_dir / "child.pyi").write_text(
        "from missing import MissingParent\n"
        "from mixin import Mixin\n"
        "from parent import Parent\n\n"
        "class Multiple(Parent, Mixin): ...\n\n"
        "class Unresolved(MissingParent): ...\n",
        encoding="utf-8",
    )

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "parent.pyi").write_text("class Parent: ...\n", encoding="utf-8")
    (target_dir / "mixin.pyi").write_text("class Mixin: ...\n", encoding="utf-8")
    child_target = target_dir / "child.pyi"
    child_target.write_text(
        "from _typeshed import Incomplete\n\n"
        "class Multiple:\n"
        "    def read(self, *args, **kwargs) -> Incomplete: ...\n\n"
        "class Unresolved:\n"
        "    def read(self, *args, **kwargs) -> Incomplete: ...\n",
        encoding="utf-8",
    )

    enrich_folder(source_dir, target_dir, write_back=True, copy_params=True)

    merged = child_target.read_text(encoding="utf-8")
    assert "class Multiple(Parent, Mixin):" in merged
    assert "class Unresolved(MissingParent):" in merged
    assert merged.count("def read(self, *args, **kwargs) -> Incomplete") == 2


def test_enrich_keeps_complete_child_method_group_and_is_idempotent(tmp_path):
    source = tmp_path / "module-doc.pyi"
    source.write_text(
        "class Child(Parent): ...\n\nclass Parent:\n    def read(self, nbytes: int, /) -> bytes: ...\n",
        encoding="utf-8",
    )
    target = tmp_path / "module.pyi"
    target.write_text(
        "from typing import Any, overload\n\n"
        "class Child:\n"
        "    @overload\n"
        "    def read(self, nbytes: int, /) -> bytes: ...\n"
        "    def read(self, *args, **kwargs) -> Any: ...\n\n"
        "class Parent:\n"
        "    def read(self, *args, **kwargs) -> Any: ...\n",
        encoding="utf-8",
    )

    list(enrich_file(source, target, write_back=True, copy_params=True))
    first_merged = target.read_text(encoding="utf-8")
    list(enrich_file(source, target, write_back=True, copy_params=True))

    assert target.read_text(encoding="utf-8") == first_merged
    assert "class Child(Parent):" in first_merged
    assert "@overload\n    def read(self, nbytes: int, /) -> bytes" in first_merged
    assert "def read(self, *args, **kwargs) -> Any" in first_merged


def test_enrich_cache_invalidates_child_when_parent_contract_changes(monkeypatch, tmp_path):
    cache_cfg.get_cache.cache_clear()
    monkeypatch.setattr(cache_cfg, "CACHE_ENABLED", True)
    monkeypatch.setattr(cache_cfg, "CACHE_DIR", str(tmp_path / "cache"))

    source_dir = tmp_path / "source"
    source_dir.mkdir()
    parent_source = source_dir / "parent.pyi"
    parent_source.write_text(
        "class Parent:\n    def read(self, nbytes: int, /) -> bytes: ...\n",
        encoding="utf-8",
    )
    (source_dir / "child.pyi").write_text(
        "from parent import Parent\n\nclass Child(Parent): ...\n",
        encoding="utf-8",
    )

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "parent.pyi").write_text("class Parent: ...\n", encoding="utf-8")
    child_target = target_dir / "child.pyi"
    original_child = "from _typeshed import Incomplete\n\nclass Child:\n    def read(self, *args, **kwargs) -> Incomplete: ...\n"
    child_target.write_text(original_child, encoding="utf-8")

    try:
        enrich_folder(source_dir, target_dir, write_back=True, copy_params=True)
        first_merged = child_target.read_text(encoding="utf-8")
        assert "def read" not in first_merged
        assert "class Child(Parent): ..." in first_merged
        compile(first_merged, str(child_target), "exec")
        first_stats = cache_cfg.cache_stats("enrich")

        child_target.write_text(original_child, encoding="utf-8")
        parent_source.write_text(
            "class Parent:\n    def read(self, nbytes: int, /) -> bytes: ...\n\nclass Unrelated:\n    value: int\n",
            encoding="utf-8",
        )
        enrich_folder(source_dir, target_dir, write_back=True, copy_params=True)
        second_stats = cache_cfg.cache_stats("enrich")

        assert second_stats["hits"] == first_stats["hits"] + 1
        assert "def read" not in child_target.read_text(encoding="utf-8")

        child_target.write_text(original_child, encoding="utf-8")
        parent_source.write_text(
            "class Parent:\n    def read(self, *args, **kwargs) -> Incomplete: ...\n\nclass Unrelated:\n    value: int\n",
            encoding="utf-8",
        )
        enrich_folder(source_dir, target_dir, write_back=True, copy_params=True)

        assert "def read(self, *args, **kwargs) -> Incomplete" in child_target.read_text(encoding="utf-8")
    finally:
        cache_cfg.get_cache("enrich").close()
        cache_cfg.get_cache.cache_clear()


def test_enrich_file(tmp_path):
    target_file = tmp_path / "target.pyi"
    target_file.touch()
    source_file = tmp_path / "source.pyi"
    source_file.touch()
    with pytest.raises(FileNotFoundError):
        list(enrich_file(source_file, target_file))
