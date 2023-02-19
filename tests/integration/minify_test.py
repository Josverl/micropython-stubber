from pathlib import Path
from types import SimpleNamespace
import pytest
from pytest_mock import MockerFixture

import stubber.minify as minify


@pytest.mark.parametrize("source", ["createstubs.py", "createstubs_mem.py", "createstubs_db.py"])
@pytest.mark.slow
@pytest.mark.minify
def test_minification_py(tmp_path: Path, source: str, pytestconfig: pytest.Config):
    "python script - test creation of minified version"
    # load process.py in the same python environment
    source_path = pytestconfig.rootpath / "src" / "stubber" / "board" / source

    result = minify.minify(source=source_path, target=tmp_path)
    assert result == 0
    # now test that log statements have been removed
    with open(tmp_path / source) as f:
        content = f.readlines()
    for line in content:
        assert line.find("._log") == -1, "all references to ._log have been removed"


@pytest.mark.parametrize("source", ["createstubs.py", "createstubs_mem.py", "createstubs_db.py"])
@pytest.mark.mocked
@pytest.mark.minify
def test_minification_quick(tmp_path: Path, source: str, mocker: MockerFixture, pytestconfig: pytest.Config):
    "test the rest of the minification functions using mocks to reduce the time needed"
    # load process.py in the same python environment
    source_path = pytestconfig.rootpath / "src" / "stubber" / "board" / source

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
    result = minify.minify(source=source_path, target=tmp_path)
    assert result == 0
    m_minify.assert_called_once()
    assert m_spr.call_count == 0  # no calls to cross compile

    # -----------------------------------------
    m_minify.reset_mock()
    m_spr.reset_mock()
    result = minify.minify(source=source_path, target=tmp_path, keep_report=False)
    assert result == 0
    m_minify.assert_called_once()
    assert m_spr.call_count == 0  # no calls to cross compile

    # -----------------------------------------
    m_minify.reset_mock()
    m_spr.reset_mock()
    result = minify.minify(source=source_path, target=tmp_path, keep_report=False, diff=True)
    assert result == 0
    m_minify.assert_called_once()
    assert m_spr.call_count == 0
    # -----------------------------------------
