import os
import sys
from pathlib import Path

import pytest
# pylint: disable=wrong-import-position,import-error
import stubber.basicgit as git
# Module Under Test
import stubber.get_mpy as get_mpy
import stubber.utils as utils
from stubber.utils.repos import switch

if not sys.warnoptions:
    import os
    import warnings

    warnings.simplefilter("default")  # Change the filter in this process
    os.environ["PYTHONWARNINGS"] = "default"  # Also affect subprocesses

from mock import MagicMock
# Mostly: No Mocks, does actual extraction from repro
from pytest_mock import MockerFixture


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


def test_one_manifest_uasync(tmp_path: Path, testrepo_micropython: Path, testrepo_micropython_lib: Path):
    "test if task.py is included with the uasyncio frozen module"
    mpy_version = "v1.18"
    mpy_folder = testrepo_micropython.absolute().as_posix()
    lib_folder = testrepo_micropython_lib.absolute().as_posix()
    stub_folder = tmp_path.absolute().as_posix()

    switch(mpy_version, mpy_path=testrepo_micropython, mpy_lib_path=testrepo_micropython_lib)

    manifest = Path(mpy_folder + "/ports/esp32/boards/manifest.py")
    get_mpy.get_frozen_from_manifest([manifest.as_posix()], stub_folder, mpy_folder, lib_folder, mpy_version)

    assert (tmp_path / "esp32/GENERIC" / "uasyncio/task.py").exists()
    # check if the task.py is included


@pytest.mark.skipif(os.getenv("CI", "local") != "local", reason="cant test in CI/CD")
# @pytest.mark.slow
@pytest.mark.parametrize(
    "mpy_version",
    [
        "v1.16",
        "v1.18",
        "v1.19",
        "v1.19.1",
        "master",
        "latest",
    ],
)
def test_freezer_mpy_manifest(
    mpy_version: str,
    testrepo_micropython: Path,
    testrepo_micropython_lib: Path,
    tmp_path: Path,
):
    "test if we can freeze source using manifest.py files"
    print(f"Testing {mpy_version} in {tmp_path}")
    switch(mpy_version, mpy_path=testrepo_micropython, mpy_lib_path=testrepo_micropython_lib)
    if mpy_version in ["master",'latest']:
        pytest.skip("TODO: need update for new manifest processing")

    get_mpy.get_frozen(str(tmp_path), version=mpy_version, mpy_path=testrepo_micropython, lib_path=testrepo_micropython_lib)
    scripts = list(tmp_path.rglob("*.py"))

    assert scripts is not None, "can freeze scripts from manifest"
    assert len(scripts) > 10, "expect at least 50 files, only found {}".format(len(scripts))

    # result = utils.generate_pyi_files(tmp_path)
    # assert result == True


# Some mocked tests to improve the coverage
def test_freezer_mpy_manifest_mocked(
    tmp_path: Path,
    testrepo_micropython: Path,
    testrepo_micropython_lib: Path,
    mocker: MockerFixture,
):
    "mocked test if we can freeze source using manifest.py files"
    mpy_version: str = "master"

    mock_get_frozen_from: MagicMock = mocker.patch("stubber.get_mpy.get_frozen_from_manifest", autospec=True, return_value=0)
    get_frozen_folders: MagicMock = mocker.patch("stubber.get_mpy.get_frozen_folders", autospec=True)
    mpy_folder = testrepo_micropython.as_posix()
    lib_folder = testrepo_micropython_lib.as_posix()

    # call with folders
    mock_glob: MagicMock = mocker.patch(
        "stubber.get_mpy.glob.glob",
        autospec=True,
        return_value=[Path("./repos/micropython/ports\\esp32\\boards\\manifest.py")],
    )

    get_mpy.get_frozen(str(tmp_path), version=mpy_version, mpy_path=mpy_folder, lib_path=lib_folder)
    assert get_frozen_folders.called == 0
    assert mock_get_frozen_from.called
    assert mock_glob.called


# def test_freezer_mpy_manifest_m2(
#     tmp_path: Path,
#     testrepo_micropython: Path,
#     testrepo_micropython_lib: Path,
#     mocker: MockerFixture,
# ):
#     "mocked test if we can freeze source oldstyle"

#     mpy_version: str = "master"
#     mock_get_frozen_from: MagicMock = mocker.patch("stubber.get_mpy.get_frozen_from_manifest", autospec=True, return_value=0)
#     get_frozen_folders: MagicMock = mocker.patch("stubber.get_mpy.get_frozen_folders", autospec=True)
#     mpy_path = testrepo_micropython.as_posix()
#     mpy_lib = testrepo_micropython_lib.as_posix()

#     # fake with no manifest.py folders
#     mock_glob: MagicMock = mocker.patch("stubber.get_mpy.glob.glob")

#     get_mpy.get_frozen(str(tmp_path), version=mpy_version, mpy_folder=mpy_path, lib_folder=mpy_lib)

#     get_mpy.get_frozen(str(tmp_path), version=mpy_version)
#     assert get_frozen_folders.called
#     assert mock_get_frozen_from.called == 0
#     assert mock_glob.called


# @pytest.mark.skipif(os.getenv("CI", "local") != "local", reason="cant test in CI/CD")
# @pytest.mark.basicgit
# @pytest.mark.slow
@pytest.mark.parametrize("mpy_version", ["v1.10", "v1.9.4"])
def test_freezer_mpy_folders(
    mpy_version,
    tmp_path,
    testrepo_micropython: Path,
    testrepo_micropython_lib: Path,
    mocker: MockerFixture,
):
    "test if we can freeze source using modules folders"
    stub_path = tmp_path

    switch(mpy_version, mpy_path=testrepo_micropython, mpy_lib_path=testrepo_micropython_lib)

    get_mpy.get_frozen_folders(
        stub_path,
        testrepo_micropython.as_posix(),
        lib_folder=testrepo_micropython_lib.as_posix(),
        version=mpy_version,
    )

    scripts = list(tmp_path.rglob("*.py"))
    assert scripts is not None, "can freeze scripts from manifest"
    assert len(scripts) > 10, "expect at least 10 files, only found {}".format(len(scripts))

    # TODO: add seperate tests for generate_pyi_files
    # result = utils.generate_pyi_files(tmp_path)
    # assert result == True
