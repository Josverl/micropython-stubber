import pytest

# module under test :
from stubber.commands.switch_cmd import VERSION_LIST
from stubber.utils.repos import read_micropython_lib_commits


@pytest.mark.parametrize("version", VERSION_LIST)
def test_stubber_switch_version_commit_list(version: str):
    mpy_lib_commits = read_micropython_lib_commits()
    if version != "latest" and version < "1.12.0":
        # from version 1.12.0, the commit list is not needed as micropython-lib is a submodule of micropython
        assert len(mpy_lib_commits) > 0
        assert version in mpy_lib_commits, "match"
