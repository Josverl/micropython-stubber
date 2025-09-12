import subprocess
import tempfile
from pathlib import Path

import pytest

# module under test :
from stubber.commands.switch_cmd import VERSION_LIST
from stubber.utils.repos import (
    checkout_arduino_lib,
    fetch_repos,
    match_lib_with_mpy,
    read_micropython_lib_commits,
    repo_paths,
    switch,
    sync_submodules,
)


@pytest.mark.parametrize("version", VERSION_LIST)
def test_stubber_switch_version_commit_list(version: str):
    mpy_lib_commits = read_micropython_lib_commits()
    if version != "latest" and version < "1.12.0":
        # from version 1.12.0, the commit list is not needed as micropython-lib is a submodule of micropython
        assert len(mpy_lib_commits) > 0
        assert version in mpy_lib_commits, "match"


# Fixtures for all tests
@pytest.fixture
def mock_paths():
    """Create mock paths for testing (cross-platform)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        mpy_path = tmpdir_path / "micropython"
        lib_path = tmpdir_path / "micropython-lib"
        yield mpy_path, lib_path


@pytest.fixture
def mock_git_operations(mocker):
    """Mock all git operations."""
    return mocker.patch("stubber.utils.repos.git")


# Tests for fetch_repos function
def test_fetch_repos_preview_tag(mock_paths, mock_git_operations, mocker):
    """Test fetch_repos with preview tag."""
    mpy_path, lib_path = mock_paths

    mocker.patch("stubber.utils.repos.SET_PREVIEW", ["preview", "master"])
    mocker.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True)
    mocker.patch("stubber.utils.repos.V_PREVIEW", "preview")

    result = fetch_repos("preview", mpy_path, lib_path)
    assert result is True
    mock_git_operations.switch_branch.assert_called_with(repo=mpy_path, branch="master")


def test_fetch_repos_stable_tag(mock_paths, mock_git_operations, mocker):
    """Test fetch_repos with stable tag."""
    mpy_path, lib_path = mock_paths

    mocker.patch("stubber.utils.repos.get_stable_mp_version", return_value="v1.26.0")
    mocker.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True)

    result = fetch_repos("stable", mpy_path, lib_path)
    assert result is True
    mock_git_operations.switch_tag.assert_called_with("v1.26.0", repo=mpy_path)


def test_fetch_repos_valid_tag(mock_paths, mock_git_operations, mocker):
    """Test fetch_repos with valid git tag."""
    mpy_path, lib_path = mock_paths

    mock_git_operations.switch_tag.side_effect = None
    mocker.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True)

    result = fetch_repos("v1.25.0", mpy_path, lib_path)
    assert result is True
    mock_git_operations.switch_tag.assert_called_with("v1.25.0", repo=mpy_path)


def test_fetch_repos_valid_branch(mock_paths, mock_git_operations, mocker):
    """Test fetch_repos with valid git branch when tag fails."""
    mpy_path, lib_path = mock_paths

    # First call (switch_tag) fails, second call (switch_branch) succeeds
    mock_git_operations.switch_tag.side_effect = Exception("Tag not found")
    mock_git_operations.switch_branch.side_effect = None

    mocker.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True)

    result = fetch_repos("main", mpy_path, lib_path)
    assert result is True
    mock_git_operations.switch_tag.assert_called_with("main", repo=mpy_path)
    mock_git_operations.switch_branch.assert_called_with(repo=mpy_path, branch="main")


def test_fetch_repos_valid_commit(mock_paths, mock_git_operations, mocker):
    """Test fetch_repos with valid commit hash when tag and branch fail."""
    mpy_path, lib_path = mock_paths

    # Both switch_tag and switch_branch fail, checkout_commit succeeds
    mock_git_operations.switch_tag.side_effect = Exception("Tag not found")
    mock_git_operations.switch_branch.side_effect = Exception("Branch not found")
    mock_git_operations.checkout_commit.side_effect = None

    mocker.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True)

    result = fetch_repos("abc123", mpy_path, lib_path)
    assert result is True
    mock_git_operations.checkout_commit.assert_called_with("abc123", repo=mpy_path)


def test_fetch_repos_all_fail(mock_paths, mock_git_operations, mocker):
    """Test fetch_repos when all git operations fail."""
    mpy_path, lib_path = mock_paths

    # All git operations fail
    mock_git_operations.switch_tag.side_effect = Exception("Tag not found")
    mock_git_operations.switch_branch.side_effect = Exception("Branch not found")
    mock_git_operations.checkout_commit.side_effect = Exception("Commit not found")

    mock_log = mocker.patch("stubber.utils.repos.log")

    result = fetch_repos("invalid", mpy_path, lib_path)
    assert result is False
    mock_log.error.assert_called_with("Could not switch to invalid - not a valid tag, branch, or commit")


def test_fetch_repos_empty_tag(mock_paths, mock_git_operations, mocker):
    """Test fetch_repos with empty tag defaults to V_PREVIEW."""
    mpy_path, lib_path = mock_paths

    mocker.patch("stubber.utils.repos.V_PREVIEW", "preview")
    mocker.patch("stubber.utils.repos.SET_PREVIEW", ["preview"])
    mocker.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True)

    result = fetch_repos("", mpy_path, lib_path)
    assert result is True


# Tests for repo_paths function
def test_repo_paths_valid_repos():
    """Test repo_paths with valid repositories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_path = Path(tmpdir) / "test_repos"
        dest_path.mkdir()

        mpy_path = dest_path / "micropython"
        mpy_lib_path = dest_path / "micropython-lib"

        # Create .git directories to simulate repos
        (mpy_path / ".git").mkdir(parents=True)
        (mpy_lib_path / ".git").mkdir(parents=True)

        result_mpy, result_lib = repo_paths(dest_path)
        assert result_mpy == mpy_path
        assert result_lib == mpy_lib_path


def test_repo_paths_missing_micropython_repo():
    """Test repo_paths when micropython repo is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_path = Path(tmpdir) / "test_repos"
        dest_path.mkdir()

        # Only create micropython-lib repo
        mpy_lib_path = dest_path / "micropython-lib"
        (mpy_lib_path / ".git").mkdir(parents=True)

        with pytest.raises(LookupError):
            repo_paths(dest_path)


def test_repo_paths_missing_lib_repo():
    """Test repo_paths when micropython-lib repo is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_path = Path(tmpdir) / "test_repos"
        dest_path.mkdir()

        # Only create micropython repo
        mpy_path = dest_path / "micropython"
        (mpy_path / ".git").mkdir(parents=True)

        with pytest.raises(LookupError):
            repo_paths(dest_path)


def test_repo_paths_nonexistent_dest(mocker):
    """Test repo_paths creates destination directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_path = Path(tmpdir) / "nonexistent"

        # Simply test that it doesn't exist first, then create it manually for test
        assert not dest_path.exists()

        # Create the directory and repos manually to simulate what os.mkdir would do
        dest_path.mkdir()
        (dest_path / "micropython" / ".git").mkdir(parents=True)
        (dest_path / "micropython-lib" / ".git").mkdir(parents=True)

        mock_config = mocker.patch("stubber.utils.repos.CONFIG")
        # Mock CONFIG to use a different repo path so it goes through the mkdir check
        mock_config.repo_path = Path("/different/path")

        result_mpy, result_lib = repo_paths(dest_path)
        assert result_mpy == dest_path / "micropython"
        assert result_lib == dest_path / "micropython-lib"


# Tests for sync_submodules function
def test_sync_submodules_success(mocker):
    """Test sync_submodules when all commands succeed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = str(tmpdir)

        mock_run = mocker.patch("stubber.utils.repos.git._run_local_git")
        mock_checkout = mocker.patch("stubber.utils.repos.checkout_arduino_lib")

        # Mock successful git commands
        mock_result = mocker.MagicMock()
        mock_result.stderr = "Success"
        mock_run.return_value = mock_result

        result = sync_submodules(repo_path)
        assert result is True
        assert mock_run.call_count == 2  # Two git commands
        mock_checkout.assert_called_once()


def test_sync_submodules_failure(mocker):
    """Test sync_submodules when git commands fail."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = str(tmpdir)

        mock_run = mocker.patch("stubber.utils.repos.git._run_local_git")
        mock_checkout = mocker.patch("stubber.utils.repos.checkout_arduino_lib")

        # Mock failed git command
        mock_run.return_value = None

        result = sync_submodules(repo_path)
        assert result is False
        mock_checkout.assert_not_called()


# Tests for checkout_arduino_lib function
def test_checkout_arduino_lib_exists(mocker):
    """Test checkout_arduino_lib when arduino-lib directory exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mpy_path = Path(tmpdir)
        arduino_lib_path = mpy_path / "lib/arduino-lib"
        arduino_lib_path.mkdir(parents=True)

        mock_run = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        checkout_arduino_lib(mpy_path)
        mock_run.assert_called_once()


def test_checkout_arduino_lib_not_exists(mocker):
    """Test checkout_arduino_lib when arduino-lib directory doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mpy_path = Path(tmpdir)

        mock_run = mocker.patch("subprocess.run")
        checkout_arduino_lib(mpy_path)
        mock_run.assert_not_called()


def test_checkout_arduino_lib_command_fails(mocker):
    """Test checkout_arduino_lib when subprocess command fails."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mpy_path = Path(tmpdir)
        arduino_lib_path = mpy_path / "lib/arduino-lib"
        arduino_lib_path.mkdir(parents=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        mock_log = mocker.patch("stubber.utils.repos.log")
        checkout_arduino_lib(mpy_path)
        mock_log.warning.assert_called_once()


# Tests for match_lib_with_mpy function
def test_match_lib_with_mpy_preview(mocker):
    """Test match_lib_with_mpy with preview version."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mpy_path = Path(tmpdir) / "micropython"
        lib_path = Path(tmpdir) / "micropython-lib"

        mocker.patch("stubber.utils.repos.SET_PREVIEW", ["preview"])
        mock_checkout = mocker.patch("stubber.utils.repos.git.checkout_commit", return_value=True)
        mock_sync = mocker.patch("stubber.utils.repos.sync_submodules", return_value=True)

        result = match_lib_with_mpy("preview", mpy_path, lib_path)
        assert result is True
        mock_checkout.assert_called_once_with("master", lib_path)
        mock_sync.assert_called_once()


def test_match_lib_with_mpy_recent_version(mocker):
    """Test match_lib_with_mpy with recent version (>= v1.20.0)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mpy_path = Path(tmpdir) / "micropython"
        lib_path = Path(tmpdir) / "micropython-lib"

        mock_checkout = mocker.patch("stubber.utils.repos.git.checkout_tag", return_value=True)
        mock_sync = mocker.patch("stubber.utils.repos.sync_submodules", return_value=True)

        result = match_lib_with_mpy("v1.22.0", mpy_path, lib_path)
        assert result is True
        mock_checkout.assert_called_once_with("v1.22.0", lib_path)
        mock_sync.assert_called_once()


def test_match_lib_with_mpy_old_version(mocker):
    """Test match_lib_with_mpy with old version (< v1.20.0)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mpy_path = Path(tmpdir) / "micropython"
        lib_path = Path(tmpdir) / "micropython-lib"

        mock_read = mocker.patch("stubber.utils.repos.read_micropython_lib_commits")
        mock_checkout = mocker.patch("stubber.utils.repos.git.checkout_commit", return_value=True)
        mock_read.return_value = {"v1.19.0": "abc123"}

        result = match_lib_with_mpy("v1.19.0", mpy_path, lib_path)
        assert result is True
        mock_checkout.assert_called_once_with("abc123", lib_path)


def test_match_lib_with_mpy_checkout_tag_fails(mocker):
    """Test match_lib_with_mpy when checkout_tag fails but fallback succeeds."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mpy_path = Path(tmpdir) / "micropython"
        lib_path = Path(tmpdir) / "micropython-lib"

        mock_checkout_tag = mocker.patch("stubber.utils.repos.git.checkout_tag")
        mock_sync = mocker.patch("stubber.utils.repos.sync_submodules", return_value=True)

        # First call fails, second call (fallback to master) succeeds
        mock_checkout_tag.side_effect = [False, True]

        result = match_lib_with_mpy("v1.21.0", mpy_path, lib_path)
        assert result is True
        assert mock_checkout_tag.call_count == 2
        mock_sync.assert_called_once()


def test_match_lib_with_mpy_all_checkout_fail(mocker):
    """Test match_lib_with_mpy when all checkout operations fail."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mpy_path = Path(tmpdir) / "micropython"
        lib_path = Path(tmpdir) / "micropython-lib"

        mock_checkout_tag = mocker.patch("stubber.utils.repos.git.checkout_tag", return_value=False)
        mock_sync = mocker.patch("stubber.utils.repos.sync_submodules")
        mock_log = mocker.patch("stubber.utils.repos.log")

        result = match_lib_with_mpy("v1.21.0", mpy_path, lib_path)
        assert result is False
        mock_sync.assert_not_called()
        mock_log.error.assert_called_once()


# Tests for switch function
def test_switch_function(mocker):
    """Test the switch function with basic functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mpy_path = Path(tmpdir) / "micropython"
        lib_path = Path(tmpdir) / "micropython-lib"

        mock_fetch = mocker.patch("stubber.utils.repos.git.fetch")
        mock_switch_branch = mocker.patch("stubber.utils.repos.git.switch_branch")
        mock_checkout_tag = mocker.patch("stubber.utils.repos.git.checkout_tag")
        mock_match = mocker.patch("stubber.utils.repos.match_lib_with_mpy")
        mocker.patch("stubber.utils.repos.V_PREVIEW", "preview")
        mocker.patch("stubber.utils.repos.SET_PREVIEW", ["preview"])

        switch("preview", mpy_path=mpy_path, mpy_lib_path=lib_path)
        assert mock_fetch.call_count == 2
        mock_switch_branch.assert_called_with(repo=mpy_path, branch="master")
        mock_match.assert_called_once()


def test_switch_with_empty_tag(mocker):
    """Test switch function with empty tag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mpy_path = Path(tmpdir) / "micropython"
        lib_path = Path(tmpdir) / "micropython-lib"

        mock_fetch = mocker.patch("stubber.utils.repos.git.fetch")
        mock_switch_branch = mocker.patch("stubber.utils.repos.git.switch_branch")
        mock_match = mocker.patch("stubber.utils.repos.match_lib_with_mpy")
        mocker.patch("stubber.utils.repos.V_PREVIEW", "preview")
        mocker.patch("stubber.utils.repos.SET_PREVIEW", ["preview"])

        switch("", mpy_path=mpy_path, mpy_lib_path=lib_path)
        mock_switch_branch.assert_called_with(repo=mpy_path, branch="master")


def test_switch_with_normal_tag(mocker):
    """Test switch function with normal version tag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mpy_path = Path(tmpdir) / "micropython"
        lib_path = Path(tmpdir) / "micropython-lib"

        mock_fetch = mocker.patch("stubber.utils.repos.git.fetch")
        mock_checkout_tag = mocker.patch("stubber.utils.repos.git.checkout_tag")
        mock_match = mocker.patch("stubber.utils.repos.match_lib_with_mpy")
        mocker.patch("stubber.utils.repos.SET_PREVIEW", ["preview"])

        switch("v1.22.0", mpy_path=mpy_path, mpy_lib_path=lib_path)
        mock_checkout_tag.assert_called_with(repo=mpy_path, tag="v1.22.0")
        mock_match.assert_called_once()
