import sys
import pytest

if not sys.warnoptions:
    import os, warnings

    warnings.simplefilter("default")  # Change the filter in this process
    os.environ["PYTHONWARNINGS"] = "default"  # Also affect subprocesses


# Dependencies
import stubber.basicgit as git
from stubber.utils import clean_version

# Module Under Test
import stubber.get_mpy as get_mpy


def test_get_mpy(tmp_path):

    # Use Submodules
    mpy_path = "./micropython"
    lib_path = "./micropython-lib"
    try:
        version = clean_version(git.get_tag(mpy_path) or "0.0")
    except Exception:
        warnings.warn("Could not find the micropython version Tag - assuming v1.x")
        version = "v1.x"

    assert version, "could not find micropython version"
    print("found micropython version : {}".format(version))
    # folder/{family}-{version}-frozen
    family = "micropython"
    stub_path = "{}-{}-frozen".format(family, clean_version(version, flat=True))
    get_mpy.get_frozen(str(tmp_path / stub_path), version=version, mpy_folder=mpy_path, lib_folder=lib_path)

    modules_count = len(list((tmp_path / stub_path).glob("**/modules.json")))
    stub_count = len(list((tmp_path / stub_path).glob("**/*.py")))
    if version == "v1.x":
        assert modules_count >= 4, "there should at least 4 module manifests"
        assert stub_count >= 10, "there should > 10 frozen modules"

    elif version >= "v1.15":
        assert modules_count >= 7, "there should at least 7 module manifests"
        assert stub_count >= 100, "there should > 100 frozen modules"


def test_get_version_commits():
    commits = get_mpy.read_micropython_lib_commits()
    assert commits
    assert len(commits) > 0
    # default should be "master"
    assert commits["latest"] == "master"
