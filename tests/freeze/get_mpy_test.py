import sys
from pathlib import Path

import pytest

if not sys.warnoptions:
    import os
    import warnings

    warnings.simplefilter("default")  # Change the filter in this process
    os.environ["PYTHONWARNINGS"] = "default"  # Also affect subprocesses


# Dependencies
import stubber.basicgit as git
import stubber.freeze.get_frozen as get_frozen
from stubber.utils.repos import read_micropython_lib_commits, switch
from stubber.utils.versions import clean_version


@pytest.mark.parametrize("tag, manifest_count, frozen_count", [("v1.9.4", 4, 10)])
def test_get_mpy(tmp_path, testrepo_micropython: Path, testrepo_micropython_lib: Path, tag: str, manifest_count, frozen_count):
    # set state of repos
    switch(tag=tag, mpy_path=testrepo_micropython, mpy_lib_path=testrepo_micropython_lib)

    # Use Submodules
    mpy_path = testrepo_micropython.as_posix()
    lib_path = testrepo_micropython_lib.as_posix()
    try:
        version = clean_version(git.get_tag(mpy_path) or "v1")
    except Exception:
        warnings.warn("Could not find the micropython version Tag - assuming v1.x")
        version = "v1"

    assert version, "could not find micropython version"
    print("found micropython version : {}".format(version))
    # folder/{family}-{version}-frozen
    family = "micropython"
    stub_path = "{}-{}-frozen".format(family, clean_version(version, flat=True))
    get_frozen.get_frozen((tmp_path / stub_path), version=version, mpy_path=mpy_path, mpy_lib_path=lib_path)

    modules = list((tmp_path / stub_path).glob("**/modules.json"))
    stubs = list((tmp_path / stub_path).glob("**/*.py"))

    assert len(modules) >= manifest_count, f"there should be => {manifest_count} module manifests"
    assert len(stubs) >= frozen_count, f"there should be >= {frozen_count} frozen modules"


def test_get_version_commits():
    commits = read_micropython_lib_commits()
    assert commits
    assert len(commits) > 0
    # default should be "master"
    assert commits["latest"] == "master"
