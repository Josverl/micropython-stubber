import sys
import pytest
from pathlib import Path

# Module Under Test
import get_cpython
import utils

# No Mocks, does actual extractionusing pip-install
@pytest.mark.parametrize(
    "requirements",
    [
        "requirements-core-micropython.txt",
        "requirements-core-pycopy.txt",
    ],
)
@pytest.mark.slow
def test_get_cpython(requirements, tmp_path):
    get_cpython.get_core(requirements=requirements, stub_path=tmp_path)
    stubfiles = list(tmp_path.rglob("*.py"))
    assert len(stubfiles) > 1
