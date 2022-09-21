import sys
from pathlib import Path
import subprocess
from types import SimpleNamespace
import pytest
from pytest_mock import MockerFixture
from mock import MagicMock

import stubber.minify as minify


@pytest.mark.parametrize("source", ["createstubs.py", "createstubs_mem.py", "createstubs_db.py"])
@pytest.mark.slow
def test_minification_py(tmp_path: Path, source: str):
    "python script - test creation of minified version"
    # load process.py in the same python environment
    source_path = Path("./board") / source

    result = minify.minify(source=source_path, target=tmp_path)
    assert result == 0
    # now test that log statements have been removed
    with open(tmp_path / source) as f:
        content = f.readlines()
    for line in content:
        assert line.find("._log") == -1, "all references to ._log have been removed"


@pytest.mark.parametrize("source", ["createstubs.py", "createstubs_mem.py", "createstubs_db.py"])
@pytest.mark.mocked
def test_minification_quick(tmp_path: Path, source: str, mocker: MockerFixture):
    "testthe rest of the minification functions using mocks to reduce the time needed"
    # load process.py in the same python environment
    source_path = Path("./board") / source

    m_minify = mocker.patch(
        "stubber.minify.python_minifier.minify",
        autospec=True,
        return_value="#short",
    )
    # mock subprocess run
    return_val = SimpleNamespace()
    return_val.returncode = 0
    m_spr = mocker.patch(
        "stubber.minify.subprocess.run",
        autospec=True,
        return_value=return_val,
    )

    # -----------------------------------------
    result = minify.minify(source=source_path, target=tmp_path, cross_compile=True)
    assert result == 0
    m_minify.assert_called_once()
    m_spr.assert_called_once()

    # -----------------------------------------
    m_minify.reset_mock()
    m_spr.reset_mock()
    result = minify.minify(source=source_path, target=tmp_path, cross_compile=False, keep_report=False)
    assert result == 0
    m_minify.assert_called_once()
    assert m_spr.call_count == 0

    # -----------------------------------------
    m_minify.reset_mock()
    m_spr.reset_mock()
    result = minify.minify(source=source_path, target=tmp_path, cross_compile=False, keep_report=False, diff=True)
    assert result == 0
    m_minify.assert_called_once()
    assert m_spr.call_count == 0
    # -----------------------------------------
    m_minify.reset_mock()
    m_spr.reset_mock()
    result = minify.minify(source=source_path, target=tmp_path, cross_compile=True, keep_report=False, diff=True)
    assert result == 0
    m_minify.assert_called_once()
    m_spr.assert_called_once()

