import pytest

# module under test :
from stubber.commands.switch_cmd import VERSION_LIST
from stubber.utils.repos import read_micropython_lib_commits


@pytest.mark.parametrize("version", VERSION_LIST)
def test_stubber_switch_version_commit_list(version: str):
    mpy_lib_commits = read_micropython_lib_commits()
    if version != "latest":
        assert len(mpy_lib_commits) > 0
        assert version in mpy_lib_commits, "match"
    # TODO : check latest / master
