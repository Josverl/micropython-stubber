"""
Shared Test Fixtures
"""
import sys
import pytest
from filelock import FileLock
#make sure that the source can be found
sys.path.insert(1, './src')

@pytest.fixture(scope="session")
def gitrepo_micropython(tmp_path_factory, worker_id):
    "get exclusive access to micropython repo to prevent multiple tests from interfering with each other"
    foldername = '../micropython-stubbertest'
    if not worker_id:
        # not executing in with multiple workers, just go for it
        return foldername

    # get the temp directory shared by all workers
    root_tmp_dir = tmp_path_factory.getbasetemp().parent

    fn = root_tmp_dir / "micropython.repo"
    with FileLock(str(fn) + ".lock"):
        # yield to run the test
        yield foldername

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
