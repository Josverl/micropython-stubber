import sys
import os
import pytest
import subprocess
from pathlib import Path


# make sure that the source can be found
RootPath = Path(os.getcwd())
src_path = str(RootPath / "src")
if not src_path in sys.path:
    sys.path.append(src_path)

# pylint: disable=wrong-import-position,import-error
# Module Under Test
import basicgit as git


def common_tst(tag):
    # print(tag)
    assert isinstance(tag, str), "tag must be a string"
    if tag != "latest":
        assert tag.startswith("v"), "tags start with a v"
        assert len(tag) >= 2, "tags are longer than 2 chars"


@pytest.mark.basicgit
# @pytest.mark.skip(reason="test discards uncomitted changes in top repo")
def test_get_tag_current():
    if not os.path.exists(".git"):
        pytest.skip("no git repo in current folder")
    else:
        # get tag of current repro
        tag = git.get_tag()
        common_tst(tag)


# @pytest.mark.basicgit
def test_get_tag_latest():
    repo = Path("./micropython")
    if not (repo / ".git").exists():
        pytest.skip("no git repo in current folder")

    result = subprocess.run(["git", "switch", "master", "--force"], capture_output=True, check=True, cwd=repo.as_posix())

    # get tag of current repro
    tag = git.get_tag("./micropython")
    assert tag == "latest"

@pytest.mark.basicgit
def test_get_tag_latest():
    repo = Path("./micropython")
    if not (repo / ".git").exists():
        pytest.skip("no git repo in current folder")

    result = subprocess.run(["git", "switch", "master", "--force"], capture_output=True, check=True, cwd=repo.as_posix())

    # get tag of current repro
    tag = git.get_tag("./micropython")
    assert tag == "latest"


@pytest.mark.basicgit
def test_get_failure_throws():
    with pytest.raises(Exception):
        git.get_tag(".not")


@pytest.mark.basicgit
@pytest.mark.skip(reason="test discards uncomitted changes in top repo")
def test_pull_master(testrepo_micropython):
    "test and force update to most recent"
    repo_path = testrepo_micropython
    x = git.pull(repo_path, "master")
    # Should succeed.
    assert x


@pytest.mark.basicgit
def test_get_tag_submodule(testrepo_micropython: Path):
    # get version of submodule repro
    for testcase in [
        testrepo_micropython.as_posix(),
        str(testrepo_micropython),
        ".\\micropython",
    ]:
        tag = git.get_tag(testcase)
        common_tst(tag)


@pytest.mark.basicgit
@pytest.mark.skip(reason="test discards uncomitted changes in top repo")
def test_checkout_sibling(testrepo_micropython):
    repo_path = testrepo_micropython
    x = git.get_tag(repo_path)
    assert x

    for ver in ["v1.11", "v1.9.4", "v1.12"]:
        git.checkout_tag(ver, repo=repo_path)
        assert git.get_tag(repo_path) == ver

    git.checkout_tag(x, repo=repo_path)
    assert git.get_tag(repo_path) == x, "can restore to prior version"
