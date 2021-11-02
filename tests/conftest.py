"""
Shared Test Fixtures
"""
import sys
import pytest

# from filelock import FileLock

# make sure that the source can be found
# sys.path.insert(1, "./src")

# Test repos are submodules of this repo
TESTREPO = "./micropython"
TESTLIB = "./micropython-lib"


@pytest.fixture(scope="session")
def testrepo_micropython_lib():
    "get exclusive access to micropython-lib repo to prevent multiple tests from interfering with each other"
    return TESTLIB
    # disabled parallel testing --> way too many issues introduced by this


@pytest.fixture(scope="session")
def testrepo_micropython():
    "get exclusive access to micropython repo to prevent multiple tests from interfering with each other"
    return TESTREPO
    # disabled parallel testing --> way too many issues introduced by this


@pytest.fixture(scope="session")
def gitrepo_this(tmp_path_factory, worker_id):
    "get exclusive access to this repo"
    return ".git"
    # disabled parallel testing --> way too many issues introduced by this
