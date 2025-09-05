"""
Enhanced test coverage for repos.py module to address missing line coverage.
This file is designed to work with the existing test framework.
"""

import tempfile
import unittest.mock
from pathlib import Path

import pytest

# Use the existing test approach but with better mocking to avoid GitHub API calls


@pytest.mark.mocked
class TestFetchReposEnhanced:
    """Test the enhanced fetch_repos function with different git reference types."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks to avoid GitHub API issues."""
        # Mock the problematic dependencies
        with unittest.mock.patch("mpflash.versions.get_stable_mp_version", return_value="v1.26.0"):
            with unittest.mock.patch("mpflash.versions.SET_PREVIEW", ["preview"]):
                with unittest.mock.patch("mpflash.versions.V_PREVIEW", "preview"):
                    yield

    def test_fetch_repos_preview_tag(self):
        """Test fetch_repos with preview tag to cover SET_PREVIEW condition."""
        from stubber.utils.repos import fetch_repos

        mpy_path, lib_path = Path("/tmp/micropython"), Path("/tmp/micropython-lib")

        with unittest.mock.patch("stubber.utils.repos.git") as mock_git:
            with unittest.mock.patch("stubber.utils.repos.SET_PREVIEW", ["preview", "master"]):
                with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True):
                    with unittest.mock.patch("stubber.utils.repos.V_PREVIEW", "preview"):
                        with unittest.mock.patch("stubber.utils.repos.log"):
                            mock_git.get_local_tag.return_value = "mocked-tag"

                            result = fetch_repos("preview", mpy_path, lib_path)
                            assert result is True
                            mock_git.switch_branch.assert_called_with(repo=mpy_path, branch="master")

    def test_fetch_repos_stable_tag(self):
        """Test fetch_repos with stable tag to cover stable branch."""
        from stubber.utils.repos import fetch_repos

        mpy_path, lib_path = Path("/tmp/micropython"), Path("/tmp/micropython-lib")

        with unittest.mock.patch("stubber.utils.repos.git") as mock_git:
            with unittest.mock.patch("stubber.utils.repos.get_stable_mp_version", return_value="v1.26.0"):
                with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True):
                    with unittest.mock.patch("stubber.utils.repos.log"):
                        mock_git.get_local_tag.return_value = "mocked-tag"

                        result = fetch_repos("stable", mpy_path, lib_path)
                        assert result is True
                        mock_git.switch_tag.assert_called_with("v1.26.0", repo=mpy_path)

    def test_fetch_repos_fallback_to_branch(self):
        """Test fetch_repos fallback from tag to branch."""
        from stubber.utils.repos import fetch_repos

        mpy_path, lib_path = Path("/tmp/micropython"), Path("/tmp/micropython-lib")

        with unittest.mock.patch("stubber.utils.repos.git") as mock_git:
            with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True):
                with unittest.mock.patch("stubber.utils.repos.log"):
                    mock_git.get_local_tag.return_value = "mocked-tag"
                    # First call (switch_tag) fails, second call (switch_branch) succeeds
                    mock_git.switch_tag.side_effect = Exception("Tag not found")
                    mock_git.switch_branch.return_value = None

                    result = fetch_repos("main", mpy_path, lib_path)
                    assert result is True
                    mock_git.switch_tag.assert_called_with("main", repo=mpy_path)
                    mock_git.switch_branch.assert_called_with(repo=mpy_path, branch="main")

    def test_fetch_repos_fallback_to_commit(self):
        """Test fetch_repos fallback from tag/branch to commit."""
        from stubber.utils.repos import fetch_repos

        mpy_path, lib_path = Path("/tmp/micropython"), Path("/tmp/micropython-lib")

        with unittest.mock.patch("stubber.utils.repos.git") as mock_git:
            with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True):
                with unittest.mock.patch("stubber.utils.repos.log"):
                    mock_git.get_local_tag.return_value = "mocked-tag"
                    # Both switch_tag and switch_branch fail, checkout_commit succeeds
                    mock_git.switch_tag.side_effect = Exception("Tag not found")
                    mock_git.switch_branch.side_effect = Exception("Branch not found")
                    mock_git.checkout_commit.return_value = None

                    result = fetch_repos("abc123", mpy_path, lib_path)
                    assert result is True
                    mock_git.checkout_commit.assert_called_with("abc123", repo=mpy_path)

    def test_fetch_repos_all_fail(self):
        """Test fetch_repos when all git operations fail."""
        from stubber.utils.repos import fetch_repos

        mpy_path, lib_path = Path("/tmp/micropython"), Path("/tmp/micropython-lib")

        with unittest.mock.patch("stubber.utils.repos.git") as mock_git:
            with unittest.mock.patch("stubber.utils.repos.log") as mock_log:
                mock_git.get_local_tag.return_value = "mocked-tag"
                # All git operations fail
                mock_git.switch_tag.side_effect = Exception("Tag not found")
                mock_git.switch_branch.side_effect = Exception("Branch not found")
                mock_git.checkout_commit.side_effect = Exception("Commit not found")

                result = fetch_repos("invalid", mpy_path, lib_path)
                assert result is False
                mock_log.error.assert_called_with("Could not switch to invalid - not a valid tag, branch, or commit")

    def test_fetch_repos_empty_tag(self):
        """Test fetch_repos with empty tag defaults to V_PREVIEW."""
        from stubber.utils.repos import fetch_repos

        mpy_path, lib_path = Path("/tmp/micropython"), Path("/tmp/micropython-lib")

        with unittest.mock.patch("stubber.utils.repos.git") as mock_git:
            with unittest.mock.patch("stubber.utils.repos.V_PREVIEW", "preview"):
                with unittest.mock.patch("stubber.utils.repos.SET_PREVIEW", ["preview"]):
                    with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy", return_value=True):
                        with unittest.mock.patch("stubber.utils.repos.log"):
                            mock_git.get_local_tag.return_value = "mocked-tag"

                            result = fetch_repos("", mpy_path, lib_path)
                            assert result is True


@pytest.mark.mocked
class TestReposPathsEnhanced:
    """Test the repo_paths function for better coverage."""

    def test_repo_paths_missing_micropython_repo(self):
        """Test repo_paths when micropython repo is missing."""
        from stubber.utils.repos import repo_paths

        with tempfile.TemporaryDirectory() as tmpdir:
            dest_path = Path(tmpdir) / "test_repos"
            dest_path.mkdir()

            # Only create micropython-lib repo
            mpy_lib_path = dest_path / "micropython-lib"
            (mpy_lib_path / ".git").mkdir(parents=True)

            with unittest.mock.patch("stubber.utils.repos.log"):
                with pytest.raises(LookupError):
                    repo_paths(dest_path)

    def test_repo_paths_missing_lib_repo(self):
        """Test repo_paths when micropython-lib repo is missing."""
        from stubber.utils.repos import repo_paths

        with tempfile.TemporaryDirectory() as tmpdir:
            dest_path = Path(tmpdir) / "test_repos"
            dest_path.mkdir()

            # Only create micropython repo
            mpy_path = dest_path / "micropython"
            (mpy_path / ".git").mkdir(parents=True)

            with unittest.mock.patch("stubber.utils.repos.log"):
                with pytest.raises(LookupError):
                    repo_paths(dest_path)


@pytest.mark.mocked
class TestSyncSubmodulesEnhanced:
    """Test the sync_submodules function."""

    def test_sync_submodules_failure(self):
        """Test sync_submodules when git commands fail."""
        from stubber.utils.repos import sync_submodules

        with unittest.mock.patch("stubber.utils.repos.git._run_local_git") as mock_run:
            with unittest.mock.patch("stubber.utils.repos.checkout_arduino_lib") as mock_checkout:
                with unittest.mock.patch("stubber.utils.repos.log"):
                    # Mock failed git command
                    mock_run.return_value = None

                    result = sync_submodules("/tmp/repo")
                    assert result is False
                    mock_checkout.assert_not_called()


@pytest.mark.mocked
class TestCheckoutArduinoLibEnhanced:
    """Test the checkout_arduino_lib function."""

    def test_checkout_arduino_lib_command_fails(self):
        """Test checkout_arduino_lib when subprocess command fails."""
        from stubber.utils.repos import checkout_arduino_lib

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


@pytest.mark.mocked
class TestMatchLibWithMpyEnhanced:
    """Test the match_lib_with_mpy function for better coverage."""

    def test_match_lib_with_mpy_checkout_tag_fails_fallback_fails(self):
        """Test match_lib_with_mpy when all checkout operations fail."""
        from stubber.utils.repos import match_lib_with_mpy

        with unittest.mock.patch("stubber.utils.repos.git.checkout_tag", return_value=False) as mock_checkout_tag:
            with unittest.mock.patch("stubber.utils.repos.sync_submodules") as mock_sync:
                with unittest.mock.patch("stubber.utils.repos.log") as mock_log:
                    result = match_lib_with_mpy("v1.21.0", Path("/tmp/mpy"), Path("/tmp/lib"))
                    assert result is False
                    mock_sync.assert_not_called()
                    mock_log.error.assert_called_once()

    def test_match_lib_with_mpy_preview_checkout_fails(self):
        """Test match_lib_with_mpy with preview version when checkout fails."""
        from stubber.utils.repos import match_lib_with_mpy

        with unittest.mock.patch("stubber.utils.repos.SET_PREVIEW", ["preview"]):
            with unittest.mock.patch("stubber.utils.repos.git.checkout_commit", return_value=False) as mock_checkout:
                with unittest.mock.patch("stubber.utils.repos.sync_submodules") as mock_sync:
                    with unittest.mock.patch("stubber.utils.repos.log") as mock_log:
                        result = match_lib_with_mpy("preview", Path("/tmp/mpy"), Path("/tmp/lib"))
                        assert result is False
                        mock_checkout.assert_called_once_with("master", Path("/tmp/lib"))
                        mock_sync.assert_not_called()
                        mock_log.error.assert_called_once()


@pytest.mark.mocked
class TestSwitchEnhanced:
    """Test the switch function for additional coverage."""

    def test_switch_with_master_tag(self):
        """Test switch function with master tag."""
        from stubber.utils.repos import switch

        with unittest.mock.patch("stubber.utils.repos.git.fetch") as mock_fetch:
            with unittest.mock.patch("stubber.utils.repos.git.switch_branch") as mock_switch_branch:
                with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy") as mock_match:
                    with unittest.mock.patch("stubber.utils.repos.V_PREVIEW", "preview"):
                        with unittest.mock.patch("stubber.utils.repos.SET_PREVIEW", ["preview"]):
                            switch("master", mpy_path=Path("/tmp/mpy"), mpy_lib_path=Path("/tmp/lib"))
                            assert mock_fetch.call_count == 2
                            mock_switch_branch.assert_called_with(repo=Path("/tmp/mpy"), branch="master")
                            mock_match.assert_called_once()

    def test_switch_with_normal_tag(self):
        """Test switch function with normal version tag."""
        from stubber.utils.repos import switch

        with unittest.mock.patch("stubber.utils.repos.git.fetch") as mock_fetch:
            with unittest.mock.patch("stubber.utils.repos.git.checkout_tag") as mock_checkout_tag:
                with unittest.mock.patch("stubber.utils.repos.match_lib_with_mpy") as mock_match:
                    with unittest.mock.patch("stubber.utils.repos.SET_PREVIEW", ["preview"]):
                        switch("v1.22.0", mpy_path=Path("/tmp/mpy"), mpy_lib_path=Path("/tmp/lib"))
                        mock_checkout_tag.assert_called_with(repo=Path("/tmp/mpy"), tag="v1.22.0")
                        mock_match.assert_called_once()
