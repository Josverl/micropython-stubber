"""
Shared Test Fixtures
"""

import builtins
import logging
import os
import sys
from pathlib import Path

import pytest
from _pytest.config import Config

# config
from stubber.utils.config import CONFIG

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # encoding="utf-8", on 3.10 only

# make sure that the source can be found, but not twice
RootPath = Path(os.getcwd())
src_path = str(RootPath / "src")
if not src_path in sys.path:
    sys.path.append(src_path)


@pytest.fixture(autouse=True, scope="session")
def _disable_stubber_caches():
    """Disable the on-disk stubber caches (enrich + stubgen) during the test run.

    These caches are content-addressable and persist across runs in a shared temp
    directory. Leaving them enabled during tests could make results depend on prior
    runs or mask regressions, so they are turned off for deterministic tests.
    """
    from stubber.utils import cache as cache_cfg

    previous = cache_cfg.CACHE_ENABLED
    cache_cfg.CACHE_ENABLED = False
    yield
    cache_cfg.CACHE_ENABLED = previous



@pytest.fixture()
def fx_add_board_path(pytestconfig: Config):
    "add ./board path temporarily"
    source_path = str(pytestconfig.rootpath / "board")
    if not source_path in sys.path:
        sys.path[1:1] = [source_path]
    yield source_path
    sys.path.remove(source_path)
    return


@pytest.fixture()
def fx_add_minified_path(pytestconfig: Config):
    "add ./minified path temporarily"
    source_path = str(pytestconfig.rootpath / "minified")
    if not source_path in sys.path:
        sys.path[1:1] = [source_path]
    yield source_path
    sys.path.remove(source_path)
    return


@pytest.fixture()
def mock_micropython_path(pytestconfig: Config):
    "Add micropython-CPython and machine to path  temporarily"
    source_path = str(pytestconfig.rootpath / "tests" / "mocks" / "micropython-cpython_core")
    machine_path = str(pytestconfig.rootpath / "tests" / "mocks" / "machine")
    original_open = builtins.open
    modules_before = set(sys.modules.keys())
    if not source_path in sys.path:
        sys.path[1:1] = [source_path, machine_path]
    yield source_path
    sys.path.remove(source_path)
    sys.path.remove(machine_path)
    builtins.open = original_open
    for mod in set(sys.modules.keys()) - modules_before:
        del sys.modules[mod]
    return


@pytest.fixture(scope="session")
def testrepo_micropython(pytestconfig: Config):
    "get path to the micropython-lib sub-repo"
    return pytestconfig.rootpath / CONFIG.mpy_path


@pytest.fixture(scope="session")
def testrepo_micropython_lib(pytestconfig: Config):
    "get path to the micropython-lib sub-repo"
    return pytestconfig.rootpath / CONFIG.mpy_lib_path


# --------------------------------------
# https://docs.pytest.org/en/stable/example/markers.html#marking-platform-specific-tests-with-pytest
ALL = set("win32 linux darwin".split())


def pytest_runtest_setup(item):
    supported_platforms = ALL.intersection(mark.name for mark in item.iter_markers())
    plat = sys.platform
    if supported_platforms and plat not in supported_platforms:
        pytest.skip("cannot run on platform {}".format(plat))
