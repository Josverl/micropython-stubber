import sys
import pytest
from pathlib import Path

# pylint: disable=wrong-import-position,import-error
import basicgit as git

# Module Under Test
import get_mpy


if not sys.warnoptions:
    import os, warnings

    warnings.simplefilter("default")  # Change the filter in this process
    os.environ["PYTHONWARNINGS"] = "default"  # Also affect subprocesses

# No Mocks, does actual extraction from repro

# TODO: allow tests to work on any path, not just my own machine


@pytest.mark.parametrize(
    "path, port, board",
    [
        (
            "C:\\develop\\MyPython\\TESTREPO-micropython\\ports\\esp32\\modules\\_boot.py",
            "esp32",
            None,
        ),
        (
            "/develop/MyPython/TESTREPO-micropython/ports/esp32/modules/_boot.py",
            "esp32",
            None,
        ),
        ("../TESTREPO-micropython/ports/esp32/modules/_boot.py", "esp32", None),
        (
            "C:\\develop\\MyPython\\TESTREPO-micropython\\ports\\stm32\\boards\\PYBV11\\modules\\_boot.py",
            "stm32",
            "PYBV11",
        ),
        (
            "/develop/MyPython/TESTREPO-micropython/ports/stm32/boards/PYBV11/modules/_boot.py",
            "stm32",
            "PYBV11",
        ),
        (
            "../TESTREPO-micropython/ports/stm32/boards/PYBV11/modules/_boot.py",
            "stm32",
            "PYBV11",
        ),
    ],
)
def test_extract_target_names(path, port, board):
    _port, _board = get_mpy.get_target_names(path)
    assert _board == board
    assert _port == port


# @pytest.mark.basicgit
@pytest.mark.slow
def test_freezer_mpy_manifest(tmp_path: Path, testrepo_micropython: Path, testrepo_micropython_lib: Path):
    "test if we can freeze source using manifest.py files"
    # mpy_path = Path(testrepo_micropython)
    # mpy_lib = Path(testrepo_micropython_lib)
    mpy_path = testrepo_micropython.as_posix()
    mpy_lib = testrepo_micropython_lib.as_posix()
    # mpy version must be at 1.12 or newer
    mpy_version = "v1.12"

    version = git.get_tag(mpy_path)
    if not version or version < mpy_version:
        git.checkout_tag(mpy_version, mpy_path)
        version = git.get_tag(mpy_path)
        assert version == mpy_version, "prep: could not checkout version {} of {}".format(mpy_version, mpy_path)

    get_mpy.get_frozen(str(tmp_path), version=mpy_version, mpy_path=mpy_path, lib_path=mpy_lib)
    scripts = list(tmp_path.rglob("*.py"))

    assert scripts is not None, "can freeze scripts from manifest"
    assert len(scripts) > 10, "expect at least 50 files, only found {}".format(len(scripts))


# @pytest.mark.basicgit
@pytest.mark.slow
def test_freezer_mpy_folders(tmp_path, testrepo_micropython: Path, testrepo_micropython_lib: Path):
    "test if we can freeze source using modules folders"
    mpy_path = testrepo_micropython.as_posix()

    # mpy version must not be older than 1.12 ( so use 1.10)
    mpy_version = "v1.10"
    version_x = version = git.get_tag(mpy_path)
    if version != mpy_version:
        git.checkout_tag(mpy_version, mpy_path)
        version = git.get_tag(mpy_path)
        assert version == mpy_version, "prep: could not checkout version {} of ./micropython".format(mpy_version)

    stub_path = tmp_path
    # freezer_mpy.get_frozen(stub_path, mpy_path, lib_path='./micropython-lib')
    get_mpy.get_frozen_folders(stub_path, mpy_path, lib_path=testrepo_micropython_lib.as_posix(), version=mpy_version)
    # restore original version
    git.checkout_tag(version_x, mpy_path)  # type:ignore
    assert True
