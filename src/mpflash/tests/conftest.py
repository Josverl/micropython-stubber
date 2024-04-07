"""Shared Pytest configuration and fixtures for mpflash tests."""

from pathlib import Path

import pytest


@pytest.fixture
def test_fw_path():
    """Return the path to the test firmware folder."""
    return Path(__file__).parent / "data" / "firmware"
