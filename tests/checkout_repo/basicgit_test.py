import sys
import os
import pytest
import subprocess
from pathlib import Path
from pytest_mock import MockerFixture
from mock import MagicMock
from subprocess import CompletedProcess

# make sure that the source can be found
RootPath = Path(os.getcwd())
src_path = str(RootPath / "src")
if not src_path in sys.path:
    sys.path.append(src_path)

# pylint: disable=wrong-import-position,import-error
# Module Under Test
import stubber.basicgit as git


def common_tst(tag):
    # print(tag)
    assert isinstance(tag, str), "tag must be a string"
    if tag != "latest":
        assert tag.startswith("v"), "tags start with a v"
        assert len(tag) >= 2, "tags are longer than 2 chars"


def test_git_clone_shallow(tmp_path):
    result = git.clone("https://github.com/micropython/micropython.git", tmp_path / "micropython")
    assert result == True


def test_git_clone(tmp_path):
    result = git.clone("https://github.com/micropython/micropython.git", tmp_path / "micropython", shallow=False)
    assert result == True


@pytest.mark.mocked
def test_git_clone_fast(mocker: MockerFixture, tmp_path):
    m_result = CompletedProcess(
        args=[
            "git",
            "clone",
            "https://github.com/micropython/micropython.git",
            "C:\\\\Users\\\\josverl\\\\AppData\\\\Local\\\\Temp\\\\pytest-of-josverl\\\\pytest-225\\\\test_git_clone0\\\\micropython",
        ],
        returncode=0,
    )

    mock: MagicMock = mocker.MagicMock(return_value=m_result)
    mocker.patch("stubber.basicgit.subprocess.run", mock)

    result = git.clone("https://github.com/micropython/micropython.git", tmp_path / "micropython", shallow=False)
    assert result == True

    result = git.clone("https://github.com/micropython/micropython.git", tmp_path / "micropython", shallow=True)
    assert result == True

    result = git.clone("https://github.com/micropython/micropython.git", tmp_path / "micropython", shallow=True, tag="latest")
    assert result == True

    result = git.clone("https://github.com/micropython/micropython.git", tmp_path / "micropython", shallow=True, tag="foobar")
    assert result == True


# @pytest.mark.basicgit
# @pytest.mark.skip(reason="test discards uncomitted changes in top repo")
def test_get_tag_current():
    if not os.path.exists(".git"):
        pytest.skip("no git repo in current folder")
    else:
        # get tag of current repro
        tag = git.get_local_tag()
        common_tst(tag)


def test_get_tags():
    # get tag of current repro
    # requires that this repo has at least a v1.3 tag
    tags = git.get_local_tags(minver="v1.3")
    assert isinstance(tags, list)
    assert len(tags) > 0
    for tag in tags:
        assert tag.startswith("v")
        assert len(tag) >= 2
        assert "." in tag


@pytest.mark.basicgit
def test_get_tag_latest():
    repo = Path("./repo/micropython")
    if not (repo / ".git").exists():
        pytest.skip("no git repo in current folder")

    result = subprocess.run(["git", "switch", "main", "--force"], capture_output=True, check=True, cwd=repo.as_posix())

    assert result.stderr == 0
    # get tag of current repro
    tag = git.get_local_tag("./repo/micropython")
    assert tag == "latest"


@pytest.mark.basicgit
@pytest.mark.skip(reason="....")
def test_get_failure_throws():
    with pytest.raises(Exception):
        git.get_local_tag(".not")


@pytest.mark.basicgit
@pytest.mark.skip(reason="test discards uncomitted changes in top repo")
def test_pull_main(testrepo_micropython):
    "test and force update to most recent"
    repo_path = testrepo_micropython
    x = git.pull(repo_path, "main")
    # Should succeed.
    assert x


@pytest.mark.basicgit
def test_get_tag_submodule(testrepo_micropython: Path):
    # get version of submodule repro
    for testcase in [
        testrepo_micropython.as_posix(),
        str(testrepo_micropython),
    ]:
        tag = git.get_local_tag(testcase)
        common_tst(tag)


@pytest.mark.basicgit
@pytest.mark.skip(reason="test discards uncomitted changes in top repo")
def test_checkout_sibling(testrepo_micropython):
    repo_path = testrepo_micropython
    x = git.get_local_tag(repo_path)
    assert x

    for ver in ["v1.11", "v1.9.4", "v1.12"]:
        git.checkout_tag(ver, repo=repo_path)
        assert git.get_local_tag(repo_path) == ver

    git.checkout_tag(x, repo=repo_path)
    assert git.get_local_tag(repo_path) == x, "can restore to prior version"


@pytest.mark.basicgit
@pytest.mark.skip()
def test_fetch():
    with pytest.raises(NotADirectoryError):
        git.fetch(repo=None)  # type: ignore

    git.fetch(repo=".")


@pytest.mark.mocked
def test_run_git_fails(mocker: MockerFixture):
    "test what happens if _run_git fails"

    mock_run_git = mocker.patch("stubber.basicgit._run_local_git", autospec=True, return_value=None)

    # fail to fetch
    r = git.fetch(repo=".")
    assert r == False
    mock_run_git.assert_called_once()

    # fail to get tag
    mock_run_git.reset_mock()
    r = git.get_local_tag()
    mock_run_git.assert_called_once()
    assert r == None

    # fail to checkout tag
    mock_run_git.reset_mock()
    r = git.checkout_tag("v1.10")
    mock_run_git.assert_called_once()
    assert r == False

    # fail to checkout commit
    mock_run_git.reset_mock()
    r = git.checkout_commit(commit_hash="123")
    mock_run_git.assert_called_once()
    assert r == False

    # fail to switch tag
    mock_run_git.reset_mock()
    r = git.switch_tag(tag="v1.10")
    mock_run_git.assert_called_once()
    assert r == False

    # fail to switch branch
    mock_run_git.reset_mock()
    r = git.switch_branch(branch="foobar")
    mock_run_git.assert_called_once()
    assert r == False
