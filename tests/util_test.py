# others
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
from pytest_mock import MockerFixture

# SOT
import stubber.utils as utils

pytestmark = [pytest.mark.stubber]

# make stub file
def test_make_stub_files_OK(tmp_path, pytestconfig):
    source = pytestconfig.rootpath / "tests/data/stubs-ok"
    dest = tmp_path / "stubs"
    shutil.copytree(source, dest)
    # -------------
    result = utils.generate_pyi_files(dest)
    # -------------
    assert result == True
    py_count = len(list(Path(dest).glob("**/*.py")))
    pyi_count = len(list(Path(dest).glob("**/*.pyi")))
    assert py_count == pyi_count, "1:1 py:pyi"
    # for py missing pyi:
    py_files = list(dest.rglob("*.py"))
    pyi_files = list(dest.rglob("*.pyi"))
    for pyi in pyi_files:
        # remove all py files  from list that have been stubbed successfully
        try:
            py_files.remove(pyi.with_suffix(".py"))
        except ValueError:
            pass
    assert not py_files, "py and pyi files should match 1:1 and stored in the same folder"


# post processing
#
@pytest.mark.mocked
def test_post_processing(tmp_path, pytestconfig, mocker: MockerFixture):
    # source = pytestconfig.rootpath / "tests/data/stubs-ok"
    dest = tmp_path / "stubs"
    # shutil.copytree(source, dest)

    m_generate_pyi_files = mocker.patch("stubber.utils.post.generate_pyi_files", autospec=True)
    return_val = SimpleNamespace()
    return_val.returncode = 0
    m_spr = mocker.patch("stubber.utils.post.subprocess.run", autospec=True, return_value=return_val)

    utils.do_post_processing([dest], stubgen=True, format=True, autoflake=False)

    m_generate_pyi_files.assert_called_once()
    m_spr.assert_called_once()


def test_stub_one_file(tmp_path, pytestconfig):
    source = pytestconfig.rootpath / "tests/data/stubs-issues"
    dest = tmp_path / "stubs"
    shutil.copytree(source, dest)
    file = list(dest.rglob("micropython.py"))[0]
    result = utils.generate_pyi_from_file(file=file)
    print(f"result : {result}")
    assert result != False


def test_stub_one_bad_file(tmp_path, pytestconfig):
    source = pytestconfig.rootpath / "tests/data/stubs-issues"
    dest = tmp_path / "stubs"
    shutil.copytree(source, dest)
    file = list(dest.rglob("machine.py"))[0]
    r = utils.generate_pyi_from_file(file=file)
    # Should not have been processed
    assert r == False


# make stub file
def test_make_stub_files_issues(tmp_path, pytestconfig):
    # Deal with some files having issues
    source = pytestconfig.rootpath / "tests/data/stubs-issues"
    dest = tmp_path / "stubs"
    shutil.copytree(source, dest)
    PROBLEMATIC = 1  # number of files with issues

    result = utils.generate_pyi_files(dest)
    assert isinstance(result, bool)
    py_count = len(list(Path(dest).glob("**/*.py")))
    pyi_count = len(list(Path(dest).glob("**/*.pyi")))

    assert py_count == pyi_count + PROBLEMATIC, "1:1 py:pyi"
    # for py missing pyi:
    py_files = list(dest.rglob("*.py"))
    pyi_files = list(dest.rglob("*.pyi"))
    for pyi in pyi_files:
        # remove all py files that have been stubbed successfully
        try:
            py_files.remove(pyi.with_suffix(".py"))
        except ValueError:
            pass

    assert len(py_files) == PROBLEMATIC, "py and pyi files should match 1:1 and stored in the same folder"
