# others
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
from mock import MagicMock
from pytest_mock import MockerFixture

# SOT
import stubber.utils as utils


@pytest.mark.parametrize(
    "commit, build, clean",
    [
        ("v1.13-103-gb137d064e", True, "v1.13-103"),
        ("v1.13", True, "v1.13"),
        ("v1.13-dirty", True, "v1.13"),
        ("v1.13-103-gb137d064e", False, "latest"),  # "v1.13-Latest"),
        ("v1.13", False, "v1.13"),
        ("v1.13-dirty", False, "latest"),  # "v1.13-Latest"),
    ],
)
def test_clean_version_build(commit, build, clean):
    assert utils.clean_version(commit, build=build) == clean


def test_clean_version_special():
    assert utils.clean_version("v1.13.0-103-gb137d064e") == "latest"
    assert utils.clean_version("v1.13.0-103-gb137d064e", build=True) == "v1.13-103"
    assert utils.clean_version("v1.13.0-103-gb137d064e", build=True, commit=True) == "v1.13-103-gb137d064e"
    # with path
    #    assert utils.clean_version("v1.13.0-103-gb137d064e", patch=True) == "v1.13.0-Latest"
    assert utils.clean_version("v1.13.0-103-gb137d064e", patch=True) == "latest"
    assert utils.clean_version("v1.13.0-103-gb137d064e", patch=True, build=True) == "v1.13.0-103"
    # with commit
    assert utils.clean_version("v1.13.0-103-gb137d064e", patch=True, build=True, commit=True) == "v1.13.0-103-gb137d064e"
    # FLats
    #    assert utils.clean_version("v1.13.0-103-gb137d064e", flat=True) == "v1_13-Latest"
    assert utils.clean_version("v1.13.0-103-gb137d064e", flat=True) == "latest"
    assert utils.clean_version("v1.13.0-103-gb137d064e", build=True, commit=True, flat=True) == "v1_13-103-gb137d064e"

    # all options , no V for version
    assert (
        utils.clean_version("v1.13.0-103-gb137d064e", patch=True, build=True, commit=True, flat=True, drop_v=True)
        == "1_13_0-103-gb137d064e"
    )

@pytest.mark.parametrize(
    "input, expected",
    [
        ("-","-"),
        ("0.0" ,"v0.0"),
        ("1.9.3" ,"v1.9.3"),
        ("v1.9.3" ,"v1.9.3"),
        ("v1.10.0" ,"v1.10"),
        ("v1.13.0" ,"v1.13"),
        ("1.13.0" ,"v1.13"),
        ("v1.20.0" ,"v1.20.0"),
        ("1.20.0" ,"v1.20.0"),
    ]
)   
def test_clean_version(input:str, expected:str):
    assert utils.clean_version(input) == expected



# make stub file
def test_make_stub_files_OK(tmp_path, pytestconfig):
    source = pytestconfig.rootpath / "tests/data/stubs-ok"
    dest = tmp_path / "stubs"
    shutil.copytree(source, dest)
    result = utils.generate_pyi_files(dest)
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
    assert len(py_files) == 0, "py and pyi files should match 1:1 and stored in the same folder"


# post processing
#
@pytest.mark.mocked
def test_post_processing(tmp_path, pytestconfig, mocker: MockerFixture):
    # source = pytestconfig.rootpath / "tests/data/stubs-ok"
    dest = tmp_path / "stubs"
    # shutil.copytree(source, dest)

    m_generate_pyi_files: MagicMock = mocker.patch("stubber.utils.post.generate_pyi_files", autospec=True)
    return_val = SimpleNamespace()
    return_val.returncode = 0
    m_spr: MagicMock = mocker.patch("stubber.utils.post.subprocess.run", autospec=True, return_value=return_val)

    utils.do_post_processing([dest], pyi=True, black=True)

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
