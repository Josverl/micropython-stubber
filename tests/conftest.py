"""
Shared Test Fixtures
"""
import sys
import pytest

# make sure that the source can be found
sys.path.insert(1, "./src")

TESTREPO = "../TESTREPO-micropython"
TESTLIB = "../TESTREPO-micropython-lib"


@pytest.fixture(scope="session")
def testrepo_micropython_lib():
    "get exclusive access to micropython-lib repo to prevent multiple tests from interfering with each other"
    return TESTLIB


@pytest.fixture(scope="session")
def testrepo_micropython():
    "get exclusive access to micropython repo to prevent multiple tests from interfering with each other"
    return TESTREPO
