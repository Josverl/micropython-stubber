"""Shared Pytest configuration and fixtures for mpflash tests."""

import sys
from pathlib import Path

import pytest


@pytest.fixture
def test_fw_path():
    """Return the path to the test firmware folder."""
    return Path(__file__).parent / "data" / "firmware"


# --------------------------------------
# https://docs.pytest.org/en/stable/example/markers.html#marking-platform-specific-tests-with-pytest
ALL_OS = set("win32 linux darwin".split())


def pytest_runtest_setup(item):
    supported_platforms = ALL_OS.intersection(mark.name for mark in item.iter_markers())
    platform = sys.platform
    if supported_platforms and platform not in supported_platforms:
        pytest.skip("cannot run on platform {}".format(platform))
