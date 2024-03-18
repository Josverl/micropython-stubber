import os
from pathlib import Path

import pytest
from mock import MagicMock

# Mostly: No Mocks, does actual extraction from repro
from pytest_mock import MockerFixture

from stubber.freeze.common import get_portboard
from stubber.freeze.freeze_folder import freeze_folders

# from stubber.freeze.freeze_manifest_1 import freeze_one_manifest_1
from stubber.freeze.freeze_manifest_2 import freeze_one_manifest_2

# Module Under Test
from stubber.freeze.get_frozen import freeze_any, get_manifests
from stubber.publish.defaults import GENERIC_L, GENERIC_U
from stubber.utils.repos import switch

pytestmark = [pytest.mark.stubber]


@pytest.mark.parametrize(
    "path, port, board",
    [
        (
            "C:\\develop\\MyPython\\repos\\micropython\\ports\\esp32\\modules\\_boot.py",
            "esp32",
            "",
        ),
        (
            "/develop/MyPython/repos/micropython/ports/esp32/modules/_boot.py",
            "esp32",
            "",
        ),
        ("./repos/micropython/ports/esp32/modules/_boot.py", "esp32", ""),
        (
            "C:\\develop\\MyPython\\repos\\micropython\\ports\\stm32\\boards\\PYBV11\\modules\\_boot.py",
            "stm32",
            "PYBV11",
        ),
        (
            "/develop/MyPython/repos/micropython/ports/stm32/boards/PYBV11/modules/_boot.py",
            "stm32",
            "PYBV11",
        ),
        (
            "./repos/micropython/ports/stm32/boards/PYBV11/modules/_boot.py",
            "stm32",
            "PYBV11",
        ),
    ],
)
def test_get_portboard(path: str, port: str, board: str):
    _port, _board = get_portboard(Path(path))
    assert _board == board
    assert _port == port


def test_manifest_uasync(tmp_path: Path, testrepo_micropython: Path, testrepo_micropython_lib: Path):
    "test if task.py is included with the uasyncio frozen module"
    mpy_version = "v1.18"
    mpy_folder = testrepo_micropython.absolute()
    lib_folder = testrepo_micropython_lib.absolute()
    stub_folder = tmp_path.absolute()

    switch(mpy_version, mpy_path=testrepo_micropython, mpy_lib_path=testrepo_micropython_lib)

    manifest = mpy_folder / "ports/esp32/boards/manifest.py"
    freeze_one_manifest_2(manifest, stub_folder, mpy_folder, lib_folder, mpy_version)

    assert (tmp_path / "esp32" / GENERIC_U / "uasyncio/task.py").exists(), "task.py must be included in uasyncio"


#######################################################################################################################
# frozen files in folders < v1.12
#######################################################################################################################


# @pytest.mark.skipif(os.getenv("CI", "local") != "local", reason="cant test in CI/CD")
# @pytest.mark.basicgit
# @pytest.mark.slow
@pytest.mark.parametrize("mpy_version", ["v1.10", "v1.9.4"])
def test_freeze_folders(
    mpy_version: str,
    tmp_path: Path,
    testrepo_micropython: Path,
    testrepo_micropython_lib: Path,
    mocker: MockerFixture,
):
    "test if we can freeze source using modules folders"
    stub_path = tmp_path

    switch(mpy_version, mpy_path=testrepo_micropython, mpy_lib_path=testrepo_micropython_lib)

    freeze_folders(
        stub_path.as_posix(),
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


#######################################################################################################################
# manifest v1 , micropython v1.12 - v1.19
#######################################################################################################################
# @pytest.mark.skipif(os.getenv("CI", "local") != "local", reason="cant test in CI/CD")
# # @pytest.mark.slow
# @pytest.mark.parametrize(
#     "mpy_version",
#     [
#         "v1.12",
#         "v1.16",
#         "v1.18",
#         "v1.19",
#     ],
# )
# # @pytest.mark.slow
# def test_freeze_one_manifest_v1(
#     mpy_version: str,
#     testrepo_micropython: Path,
#     testrepo_micropython_lib: Path,
#     tmp_path: Path,
# ):
#     "test if task.py is included with the uasyncio frozen module"
#     mpy_folder = testrepo_micropython.absolute()
#     lib_folder = testrepo_micropython_lib.absolute()
#     stub_folder = tmp_path.absolute()

#     switch(mpy_version, mpy_path=testrepo_micropython, mpy_lib_path=testrepo_micropython_lib)

#     manifest = mpy_folder / "ports/esp32/boards/manifest.py"
#     freeze_one_manifest_1(manifest, stub_folder, mpy_folder, lib_folder, mpy_version)
#     # todo : add more checks


#######################################################################################################################
# manifest v2 ,
#######################################################################################################################
@pytest.mark.skipif(os.getenv("CI", "local") != "local", reason="cant test in CI/CD")
# @pytest.mark.slow
@pytest.mark.parametrize(
    "mpy_version,port",
    [
        ("v1.12", "esp32"),
        ("v1.16", "esp32"),
        ("v1.18", "esp32"),
        ("v1.18", "esp8266"),
        ("v1.19", "esp32"),
    ],
)
# @pytest.mark.slow
def test_freeze_one_manifest_v2(
    mpy_version: str,
    port: str,
    testrepo_micropython: Path,
    testrepo_micropython_lib: Path,
    tmp_path: Path,
):
    "Test freezing with manifest v2"
    mpy_folder = testrepo_micropython.absolute()
    lib_folder = testrepo_micropython_lib.absolute()
    stub_folder = tmp_path.absolute()

    switch(mpy_version, mpy_path=testrepo_micropython, mpy_lib_path=testrepo_micropython_lib)

    manifest = mpy_folder / "ports" / port / "boards/manifest.py"
    freeze_one_manifest_2(manifest, stub_folder, mpy_folder, lib_folder, mpy_version)
    # todo : add more checks


#######################################################################################################################
# ANY
#######################################################################################################################


# @pytest.mark.skipif(os.getenv("CI", "local") != "local", reason="cant test in CI/CD")
# @pytest.mark.slow
@pytest.mark.parametrize(
    "mpy_version",
    [
        "v1.12",
        # "v1.16",
        # "v1.17",
        "v1.18",
        # "v1.19",
        # "v1.19.1",
        "v1.20.0",
        # "v1.21.0",
        "latest",
        "preview",
    ],
)
def test_freeze_any(
    mpy_version: str,
    testrepo_micropython: Path,
    testrepo_micropython_lib: Path,
    tmp_path: Path,
):
    "test if we can freeze source using manifest.py files"
    # print(f"Testing {mpy_version} in {tmp_path}")
    switch(mpy_version, mpy_path=testrepo_micropython, mpy_lib_path=testrepo_micropython_lib)

    freeze_any(
        tmp_path,
        version=mpy_version,
        mpy_path=testrepo_micropython,
        mpy_lib_path=testrepo_micropython_lib,
    )
    scripts = list(tmp_path.rglob("*.py"))

    assert scripts is not None, "can freeze scripts from manifest"
    assert len(scripts) > 10, "expect at least 50 files, only found {}".format(len(scripts))


#######################################################################################################################
#######################################################################################################################


# Some mocked tests to improve the coverage
# @pytest.mark.skip("fails for unknown reason in CI, TODO: fix")
@pytest.mark.parametrize(
    "mpy_version",
    [
        "master",
        "v1.12",
        "v1.16",
        # "v1.17",
        "v1.18",
        # "v1.19",
        "v1.19.1",
        "v1.20.0",
        "v1.21.0",
        "latest",
    ],
)
@pytest.mark.mocked
def test_freeze_any_mocked(
    tmp_path: Path,
    testrepo_micropython: Path,
    testrepo_micropython_lib: Path,
    mocker: MockerFixture,
    mpy_version: str,
):
    "mocked test if we can freeze source using manifest.py files"

    m_freeze_folders = mocker.patch("stubber.freeze.get_frozen.freeze_folders", autospec=True, return_value=[1])
    # m_freeze_one_manifest_1= mocker.patch("stubber.freeze.get_frozen.freeze_one_manifest_1", autospec=True, return_value=1)
    m_freeze_one_manifest_2 = mocker.patch(
        "stubber.freeze.get_frozen.freeze_one_manifest_2", autospec=True, return_value=1
    )
    x = freeze_any(
        tmp_path,
        version=mpy_version,
        mpy_path=testrepo_micropython,
        mpy_lib_path=testrepo_micropython_lib,
    )
    # calls = m_freeze_folders.call_count + m_freeze_one_manifest_1.call_count + m_freeze_one_manifest_2.call_count
    calls = m_freeze_folders.call_count + m_freeze_one_manifest_2.call_count
    print(f" m_freeze_folders.call_count {m_freeze_folders.call_count}")
    # print(f" m_freeze_one_manifest_1.call_count {m_freeze_one_manifest_1.call_count}")
    print(f" m_freeze_one_manifest_2.call_count {m_freeze_one_manifest_2.call_count}")

    # TODO: fix me
    # assert calls >= 1
    # assert x >= 1, "expect >= 1 stubs"


def test_freeze_manifest2_error_mocked(
    tmp_path: Path,
    testrepo_micropython: Path,
    testrepo_micropython_lib: Path,
    mocker: MockerFixture,
    mpy_version: str = "v1.19",
):
    "mocked test if we can freeze source using manifest.py files"

    m_freeze_folders = mocker.patch("stubber.freeze.get_frozen.freeze_folders", autospec=True, return_value=[1])
    m_freeze_one_manifest_2 = mocker.patch(
        "stubber.freeze.get_frozen.freeze_one_manifest_2", autospec=True, return_value=1
    )
    # get the correct version to test
    switch(mpy_version, mpy_path=testrepo_micropython, mpy_lib_path=testrepo_micropython_lib)
    test_path = freeze_any(
        tmp_path,
        version=mpy_version,
        mpy_path=testrepo_micropython,
        mpy_lib_path=testrepo_micropython_lib,
    )
    assert test_path is not None, "expect a path"
    # no further asserts of path as this is mocked
    assert m_freeze_folders.call_count == 0, "expect no calls to freeze_folders"
    assert m_freeze_one_manifest_2.call_count == 34, "34 calls to freeze_one_manifest_2"


##########################################################################


def test_get_manifests(
    testrepo_micropython: Path,
    testrepo_micropython_lib: Path,
    mocker: MockerFixture,
    mpy_version: str = "v1.19",
):
    switch(mpy_version, mpy_path=testrepo_micropython, mpy_lib_path=testrepo_micropython_lib)
    manifests = get_manifests(mpy_path=testrepo_micropython)
    assert isinstance(manifests, list)
    assert len(manifests) == 34, "expect 34 manifests"
    for m in manifests:
        assert isinstance(m, Path), "expect Path object"
        assert m.name == "manifest.py", "expect manifest.py"
