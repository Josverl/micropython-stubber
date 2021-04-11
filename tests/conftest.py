"""
Shared Test Fixtures
"""
import sys
import pytest
from filelock import FileLock
#make sure that the source can be found
sys.path.insert(1, './src')

TESTREPO = '../TESTREPO-micropython'
TESTLIB  = '../TESTREPO-micropython-lib'

@pytest.fixture(scope="session")
def testrepo_micropython_lib():
    "get exclusive access to micropython-lib repo to prevent multiple tests from interfering with each other"
    return TESTLIB


@pytest.fixture(scope="session")
def testrepo_micropython():
    "get exclusive access to micropython repo to prevent multiple tests from interfering with each other"
    return TESTREPO
    # disabled parallel testing --> way too many issues introduced by this
    # if not worker_id:
    #     return foldername
    #     # not executing in with multiple workers, just go for it

    # # get the temp directory shared by all workers
    # root_tmp_dir = tmp_path_factory.getbasetemp().parent

    # fn = root_tmp_dir / "micropython.repo"
    # with FileLock(str(fn) + ".lock"):
    #     # yield to run the test
    #     yield foldername

@pytest.fixture(scope="session")
def gitrepo_this(tmp_path_factory, worker_id):
    "get exclusive access to this repo"
    if not worker_id:
        # not executing in with multiple workers, just go for it
        return '.git'

    # get the temp directory shared by all workers
    root_tmp_dir = tmp_path_factory.getbasetemp().parent

    fn = root_tmp_dir / "this.repo"
    with FileLock(str(fn) + ".lock"):
        # yield to run the test
        yield '.git'
