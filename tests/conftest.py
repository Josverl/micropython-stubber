"""
Shared Test Fixtures
"""
import sys
import os
from pathlib import Path
import pytest
from _pytest.config import Config


# make sure that the source can be found

RootPath = Path(os.getcwd())
src_path = str(RootPath / "src")
if not src_path in sys.path:
    sys.path.append(src_path)


@pytest.fixture()
def add_board_path(pytestconfig: Config):
    "add ./board path temporarily"
    source_path = str(pytestconfig.rootpath / "board")
    if not source_path in sys.path:
        sys.path[1:1] = [source_path]
    yield source_path
    sys.path.remove(source_path)
    return


@pytest.fixture()
def add_minified_path(pytestconfig: Config):
    "add ./board path temporarily"
    source_path = str(pytestconfig.rootpath / "minified")
    if not source_path in sys.path:
        sys.path[1:1] = [source_path]
    yield source_path
    sys.path.remove(source_path)
    return


@pytest.fixture()
def mock_pycopy_path(pytestconfig: Config):
    "pycopy-CPython to path  temporarily"
    source_path = str(pytestconfig.rootpath / "tests" / "mocks" / "pycopy-cpython_core")
    machine_path = str(pytestconfig.rootpath / "tests" / "mocks" / "machine")
    if not source_path in sys.path:
        sys.path[1:1] = [source_path, machine_path]
    yield source_path
    sys.path.remove(source_path)
    sys.path.remove(machine_path)
    return


@pytest.fixture()
def mock_micropython_path(pytestconfig: Config):
    "micropython-CPython to path  temporarily"
    source_path = str(pytestconfig.rootpath / "tests" / "mocks" / "micropython-cpython_core")
    machine_path = str(pytestconfig.rootpath / "tests" / "mocks" / "machine")
    if not source_path in sys.path:
        sys.path[1:1] = [source_path, machine_path]
    yield source_path
    sys.path.remove(source_path)
    sys.path.remove(machine_path)
    return


@pytest.fixture(scope="session")
def testrepo_micropython(pytestconfig: Config):
    "get path to the micropython-lib sub-repo"
    root = pytestconfig.rootpath
    return pytestconfig.rootpath / "micropython"


@pytest.fixture(scope="session")
def testrepo_micropython_lib(pytestconfig: Config):
    "get path to the micropython-lib sub-repo"
    return pytestconfig.rootpath / "micropython-lib"


# --------------------------------------
# https://docs.pytest.org/en/stable/example/markers.html#marking-platform-specific-tests-with-pytest
ALL = set("win32 linux darwin".split())


def pytest_runtest_setup(item):
    supported_platforms = ALL.intersection(mark.name for mark in item.iter_markers())
    plat = sys.platform
    if supported_platforms and plat not in supported_platforms:
        pytest.skip("cannot run on platform {}".format(plat))
