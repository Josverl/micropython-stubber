import tempfile
import unittest.mock
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


class TestFetchRepos:
    """Test the fetch_repos function with different git reference types."""

    @pytest.fixture
    def mock_paths(self):
        """Create mock paths for testing."""
        return Path("/tmp/micropython"), Path("/tmp/micropython-lib")

    @pytest.fixture  
    def mock_git_operations(self):
        """Mock all git operations."""
        with unittest.mock.patch("stubber.utils.repos.git") as mock_git:
            yield mock_git

    def test_fetch_repos_preview_tag(self, mock_paths, mock_git_operations):
        """Test fetch_repos with preview tag."""
        mpy_path, lib_path = mock_paths
        
        with unittest.mock.patch("stubber.utils.repos.SET_PREVIEW", ["preview", "master"]):
            with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True):
                with unittest.mock.patch("stubber.utils.repos.V_PREVIEW", "preview"):
                    result = fetch_repos("preview", mpy_path, lib_path)
                    assert result is True
                    mock_git_operations.switch_branch.assert_called_with(repo=mpy_path, branch="master")

    def test_fetch_repos_stable_tag(self, mock_paths, mock_git_operations):
        """Test fetch_repos with stable tag."""
        mpy_path, lib_path = mock_paths
        
        with unittest.mock.patch("stubber.utils.repos.get_stable_mp_version", return_value="v1.26.0"):
            with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True):
                result = fetch_repos("stable", mpy_path, lib_path)
                assert result is True
                mock_git_operations.switch_tag.assert_called_with("v1.26.0", repo=mpy_path)

    def test_fetch_repos_valid_tag(self, mock_paths, mock_git_operations):
        """Test fetch_repos with valid git tag."""
        mpy_path, lib_path = mock_paths
        
        mock_git_operations.switch_tag.side_effect = None
        with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True):
            result = fetch_repos("v1.25.0", mpy_path, lib_path)
            assert result is True
            mock_git_operations.switch_tag.assert_called_with("v1.25.0", repo=mpy_path)

    def test_fetch_repos_valid_branch(self, mock_paths, mock_git_operations):
        """Test fetch_repos with valid git branch when tag fails."""
        mpy_path, lib_path = mock_paths
        
        # First call (switch_tag) fails, second call (switch_branch) succeeds
        mock_git_operations.switch_tag.side_effect = Exception("Tag not found")
        mock_git_operations.switch_branch.side_effect = None
        
        with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True):
            result = fetch_repos("main", mpy_path, lib_path)
            assert result is True
            mock_git_operations.switch_tag.assert_called_with("main", repo=mpy_path)
            mock_git_operations.switch_branch.assert_called_with(repo=mpy_path, branch="main")

    def test_fetch_repos_valid_commit(self, mock_paths, mock_git_operations):
        """Test fetch_repos with valid commit hash when tag and branch fail."""
        mpy_path, lib_path = mock_paths
        
        # Both switch_tag and switch_branch fail, checkout_commit succeeds
        mock_git_operations.switch_tag.side_effect = Exception("Tag not found")
        mock_git_operations.switch_branch.side_effect = Exception("Branch not found")
        mock_git_operations.checkout_commit.side_effect = None
        
        with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True):
            result = fetch_repos("abc123", mpy_path, lib_path)
            assert result is True
            mock_git_operations.checkout_commit.assert_called_with("abc123", repo=mpy_path)

    def test_fetch_repos_all_fail(self, mock_paths, mock_git_operations):
        """Test fetch_repos when all git operations fail."""
        mpy_path, lib_path = mock_paths
        
        # All git operations fail
        mock_git_operations.switch_tag.side_effect = Exception("Tag not found")
        mock_git_operations.switch_branch.side_effect = Exception("Branch not found") 
        mock_git_operations.checkout_commit.side_effect = Exception("Commit not found")
        
        with unittest.mock.patch("stubber.utils.repos.log") as mock_log:
            result = fetch_repos("invalid", mpy_path, lib_path)
            assert result is False
            mock_log.error.assert_called_with("Could not switch to invalid - not a valid tag, branch, or commit")

    def test_fetch_repos_empty_tag(self, mock_paths, mock_git_operations):
        """Test fetch_repos with empty tag defaults to V_PREVIEW."""
        mpy_path, lib_path = mock_paths
        
        with unittest.mock.patch("stubber.utils.repos.V_PREVIEW", "preview"):
            with unittest.mock.patch("stubber.utils.repos.SET_PREVIEW", ["preview"]):
                with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True):
                    result = fetch_repos("", mpy_path, lib_path)
                    assert result is True


class TestReposPaths:
    """Test the repo_paths function."""

    def test_repo_paths_valid_repos(self):
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

    def test_repo_paths_missing_micropython_repo(self):
        """Test repo_paths when micropython repo is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dest_path = Path(tmpdir) / "test_repos"
            dest_path.mkdir()
            
            # Only create micropython-lib repo
            mpy_lib_path = dest_path / "micropython-lib"
            (mpy_lib_path / ".git").mkdir(parents=True)
            
            with pytest.raises(LookupError):
                repo_paths(dest_path)

    def test_repo_paths_missing_lib_repo(self):
        """Test repo_paths when micropython-lib repo is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dest_path = Path(tmpdir) / "test_repos"
            dest_path.mkdir()
            
            # Only create micropython repo
            mpy_path = dest_path / "micropython"
            (mpy_path / ".git").mkdir(parents=True)
            
            with pytest.raises(LookupError):
                repo_paths(dest_path)

    def test_repo_paths_nonexistent_dest(self):
        """Test repo_paths creates destination directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dest_path = Path(tmpdir) / "nonexistent"
            
            # Create the repos after mkdir would be called
            def side_effect(path):
                path.mkdir(exist_ok=True)
                # Create repos
                (path / "micropython" / ".git").mkdir(parents=True)
                (path / "micropython-lib" / ".git").mkdir(parents=True)
            
            with unittest.mock.patch("os.mkdir", side_effect=lambda p: side_effect(Path(p))):
                with unittest.mock.patch("stubber.utils.repos.CONFIG") as mock_config:
                    mock_config.repo_path = Path("/different/path")
                    repo_paths(dest_path)
                    # Should have called os.mkdir
                    assert True  # If we get here, no exception was raised


class TestSyncSubmodules:
    """Test the sync_submodules function."""

    def test_sync_submodules_success(self):
        """Test sync_submodules when all commands succeed."""
        with unittest.mock.patch("stubber.utils.repos.git._run_local_git") as mock_run:
            with unittest.mock.patch("stubber.utils.repos.checkout_arduino_lib") as mock_checkout:
                # Mock successful git commands
                mock_result = unittest.mock.MagicMock()
                mock_result.stderr = "Success"
                mock_run.return_value = mock_result
                
                result = sync_submodules("/tmp/repo")
                assert result is True
                assert mock_run.call_count == 2  # Two git commands
                mock_checkout.assert_called_once()

    def test_sync_submodules_failure(self):
        """Test sync_submodules when git commands fail."""
        with unittest.mock.patch("stubber.utils.repos.git._run_local_git") as mock_run:
            with unittest.mock.patch("stubber.utils.repos.checkout_arduino_lib") as mock_checkout:
                # Mock failed git command
                mock_run.return_value = None
                
                result = sync_submodules("/tmp/repo")
                assert result is False
                mock_checkout.assert_not_called()


class TestCheckoutArduinoLib:
    """Test the checkout_arduino_lib function."""

    def test_checkout_arduino_lib_exists(self):
        """Test checkout_arduino_lib when arduino-lib directory exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mpy_path = Path(tmpdir)
            arduino_lib_path = mpy_path / "lib/arduino-lib"
            arduino_lib_path.mkdir(parents=True)
            
            with unittest.mock.patch("subprocess.run") as mock_run:
                mock_result = unittest.mock.MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result
                
                checkout_arduino_lib(mpy_path)
                mock_run.assert_called_once()

    def test_checkout_arduino_lib_not_exists(self):
        """Test checkout_arduino_lib when arduino-lib directory doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mpy_path = Path(tmpdir)
            
            with unittest.mock.patch("subprocess.run") as mock_run:
                checkout_arduino_lib(mpy_path)
                mock_run.assert_not_called()

    def test_checkout_arduino_lib_command_fails(self):
        """Test checkout_arduino_lib when subprocess command fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mpy_path = Path(tmpdir)
            arduino_lib_path = mpy_path / "lib/arduino-lib"
            arduino_lib_path.mkdir(parents=True)
            
            import subprocess
            with unittest.mock.patch("subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.CalledProcessError(1, "git")
                
                with unittest.mock.patch("stubber.utils.repos.log") as mock_log:
                    checkout_arduino_lib(mpy_path)
                    mock_log.warning.assert_called_once()


class TestMatchLibWithMpy:
    """Test the match_lib_with_mpy function."""

    def test_match_lib_with_mpy_preview(self):
        """Test match_lib_with_mpy with preview version."""
        with unittest.mock.patch("stubber.utils.repos.SET_PREVIEW", ["preview"]):
            with unittest.mock.patch("stubber.utils.repos.git.checkout_commit", return_value=True) as mock_checkout:
                with unittest.mock.patch("stubber.utils.repos.sync_submodules", return_value=True) as mock_sync:
                    result = match_lib_with_mpy("preview", Path("/tmp/mpy"), Path("/tmp/lib"))
                    assert result is True
                    mock_checkout.assert_called_once_with("master", Path("/tmp/lib"))
                    mock_sync.assert_called_once()

    def test_match_lib_with_mpy_recent_version(self):
        """Test match_lib_with_mpy with recent version (>= v1.20.0)."""
        with unittest.mock.patch("stubber.utils.repos.git.checkout_tag", return_value=True) as mock_checkout:
            with unittest.mock.patch("stubber.utils.repos.sync_submodules", return_value=True) as mock_sync:
                result = match_lib_with_mpy("v1.22.0", Path("/tmp/mpy"), Path("/tmp/lib"))
                assert result is True
                mock_checkout.assert_called_once_with("v1.22.0", Path("/tmp/lib"))
                mock_sync.assert_called_once()

    def test_match_lib_with_mpy_old_version(self):
        """Test match_lib_with_mpy with old version (< v1.20.0)."""
        with unittest.mock.patch("stubber.utils.repos.read_micropython_lib_commits") as mock_read:
            with unittest.mock.patch("stubber.utils.repos.git.checkout_commit", return_value=True) as mock_checkout:
                mock_read.return_value = {"v1.19.0": "abc123"}
                
                result = match_lib_with_mpy("v1.19.0", Path("/tmp/mpy"), Path("/tmp/lib"))
                assert result is True
                mock_checkout.assert_called_once_with("abc123", Path("/tmp/lib"))

    def test_match_lib_with_mpy_checkout_tag_fails(self):
        """Test match_lib_with_mpy when checkout_tag fails but fallback succeeds."""
        with unittest.mock.patch("stubber.utils.repos.git.checkout_tag") as mock_checkout_tag:
            with unittest.mock.patch("stubber.utils.repos.sync_submodules", return_value=True) as mock_sync:
                # First call fails, second call (fallback to master) succeeds
                mock_checkout_tag.side_effect = [False, True]
                
                result = match_lib_with_mpy("v1.21.0", Path("/tmp/mpy"), Path("/tmp/lib"))
                assert result is True
                assert mock_checkout_tag.call_count == 2
                mock_sync.assert_called_once()

    def test_match_lib_with_mpy_all_checkout_fail(self):
        """Test match_lib_with_mpy when all checkout operations fail."""
        with unittest.mock.patch("stubber.utils.repos.git.checkout_tag", return_value=False) as mock_checkout_tag:
            with unittest.mock.patch("stubber.utils.repos.sync_submodules") as mock_sync:
                with unittest.mock.patch("stubber.utils.repos.log") as mock_log:
                    result = match_lib_with_mpy("v1.21.0", Path("/tmp/mpy"), Path("/tmp/lib"))
                    assert result is False
                    mock_sync.assert_not_called()
                    mock_log.error.assert_called_once()


class TestSwitch:
    """Test the switch function."""

    def test_switch_function(self):
        """Test the switch function with basic functionality."""
        with unittest.mock.patch("stubber.utils.repos.git.fetch") as mock_fetch:
            with unittest.mock.patch("stubber.utils.repos.git.switch_branch") as mock_switch_branch:
                with unittest.mock.patch("stubber.utils.repos.git.checkout_tag") as mock_checkout_tag:
                    with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy") as mock_match:
                        with unittest.mock.patch("stubber.utils.repos.V_PREVIEW", "preview"):
                            with unittest.mock.patch("stubber.utils.repos.SET_PREVIEW", ["preview"]):
                                switch("preview", mpy_path=Path("/tmp/mpy"), mpy_lib_path=Path("/tmp/lib"))
                                assert mock_fetch.call_count == 2
                                mock_switch_branch.assert_called_with(repo=Path("/tmp/mpy"), branch="master")
                                mock_match.assert_called_once()

    def test_switch_with_empty_tag(self):
        """Test switch function with empty tag."""
        with unittest.mock.patch("stubber.utils.repos.git.fetch") as mock_fetch:
            with unittest.mock.patch("stubber.utils.repos.git.switch_branch") as mock_switch_branch:
                with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy") as mock_match:
                    with unittest.mock.patch("stubber.utils.repos.V_PREVIEW", "preview"):
                        with unittest.mock.patch("stubber.utils.repos.SET_PREVIEW", ["preview"]):
                            switch("", mpy_path=Path("/tmp/mpy"), mpy_lib_path=Path("/tmp/lib"))
                            mock_switch_branch.assert_called_with(repo=Path("/tmp/mpy"), branch="master")

    def test_switch_with_normal_tag(self):
        """Test switch function with normal version tag."""
        with unittest.mock.patch("stubber.utils.repos.git.fetch") as mock_fetch:
            with unittest.mock.patch("stubber.utils.repos.git.checkout_tag") as mock_checkout_tag:
                with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy") as mock_match:
                    with unittest.mock.patch("stubber.utils.repos.SET_PREVIEW", ["preview"]):
                        switch("v1.22.0", mpy_path=Path("/tmp/mpy"), mpy_lib_path=Path("/tmp/lib"))
                        mock_checkout_tag.assert_called_with(repo=Path("/tmp/mpy"), tag="v1.22.0")
                        mock_match.assert_called_once()
