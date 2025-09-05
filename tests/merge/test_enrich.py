from pathlib import Path

import pytest

from stubber.codemod.enrich import enrich_file, enrich_folder, package_from_path, source_target_candidates, upackage_equal


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


def test_enrich_file(tmp_path):
    target_file = tmp_path / "target.pyi"
    target_file.touch()
    source_file = tmp_path / "source.pyi"
    source_file.touch()
    with pytest.raises(FileNotFoundError):
        list(enrich_file(source_file, target_file))
