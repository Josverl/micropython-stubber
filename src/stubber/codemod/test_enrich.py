from typing import List
import pytest
from pathlib import Path
# from stubber.codemod.enrich import merge_source_candidates


@pytest.fixture
def docstub_path(tmp_path):
    # Create a temporary directory for docstub files
    docstub_path = tmp_path / "docstubs"
    docstub_path.mkdir(exist_ok=True, parents=True)

    (docstub_path / "one.pyi").touch()

    # Create some docstub files
    (docstub_path / "package.py").touch()
    (docstub_path / "package.pyi").touch()
    (docstub_path / "upackage.py").touch()
    (docstub_path / "upackage.pyi").touch()
    # for ufoo to foo
    (docstub_path / "usys.pyi").touch()
    (docstub_path / "sys.pyi").touch()
    # from _foo to foo
    (docstub_path / "rp2.pyi").touch()
    (docstub_path / "_rp2.pyi").touch()

    # dist package format
    (docstub_path / "foo").mkdir(exist_ok=True, parents=True)
    (docstub_path / "foo" / "__init__.pyi").touch()

    # dist package format
    (docstub_path / "bar").mkdir(exist_ok=True, parents=True)
    (docstub_path / "bar" / "__init__.pyi").touch()
    (docstub_path / "bar" / "barclass.pyi").touch()

    # dist package format
    (docstub_path / "machine").mkdir(exist_ok=True, parents=True)
    (docstub_path / "machine" / "__init__.pyi").touch()
    (docstub_path / "machine" / "Pin.pyi").touch()
    (docstub_path / "machine" / "Signal.pyi").touch()
    (docstub_path / "machine" / "ADC.pyi").touch()
    return docstub_path


# @pytest.mark.parametrize(
#     "package_name, expected_candidates",
#     [
#         (
#             "package",
#             [
#                 "package.py",
#                 "package.pyi",
#                 "upackage.py",
#                 "upackage.pyi",
#             ],
#         ),
#         ("usys", ["usys.pyi", "sys.pyi"]),
#         ("_rp2", ["rp2.pyi", "_rp2.pyi"]),
#         ("rp2", ["rp2.pyi"]),
#         ("nonexistent", []),
#         ("foo", ["foo/__init__.pyi"]),
#         ("ufoo", ["foo/__init__.pyi"]),
#         ("bar", ["bar/__init__.pyi", "bar/barclass.pyi"]),
#         (
#             "machine",
#             [
#                 "machine/__init__.pyi",
#                 "machine/Pin.pyi",
#                 "machine/Signal.pyi",
#                 "machine/ADC.pyi",
#             ],
#         ),
#         ("machine.Pin", ["machine/Pin.pyi"]),
#     ],
# )
# def test_merge_source_candidates(
#     package_name: str,
#     expected_candidates: List[str],
#     docstub_path: Path,
# ):
#     # Test with package name "package"
#     candidates = merge_source_candidates(package_name, docstub_path)
#     assert len(candidates) == len(expected_candidates)
#     for e in expected_candidates:
#         assert docstub_path / e in candidates

#     # todo : test ordering
