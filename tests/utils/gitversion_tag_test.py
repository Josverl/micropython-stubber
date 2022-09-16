from pathlib import Path

import pytest
from packaging.version import Version, parse
from stubber.utils.makeversionhdr import get_version_build_from_git, get_version_info_from_git


@pytest.mark.parametrize(
    "path",
    [
        Path.cwd(),
        Path("./repos/micropython"),
    ],
)
def test_get_version(path):
    """Test that we can get the version info from git"""
    git_tag, short_hash = get_version_info_from_git(path)  # type: ignore
    assert git_tag is not None
    assert short_hash is not None
    # tag should start with a v
    assert git_tag[0] == "v"
    parts = git_tag.split("-")

    if len(parts) > 2:
        # first partmust be parsed to a Version Type
        ver = parse(parts[0])
        assert isinstance(ver, Version)
    if len(parts) >= 3:
        # second part must be an integer
        assert parts[1].isnumeric()

    assert True


@pytest.mark.parametrize(
    "path",
    [
        Path.cwd(),
        Path("./repos/micropython"),
    ],
)
def test_get_version_build(path):
    """Test that we can get the version info from git"""
    version, build = get_version_build_from_git(path)
    assert isinstance(version, Version)
    if build  != "dirty":
        assert build.isnumeric()
