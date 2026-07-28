"""Shared fixtures for the freeze tests.

Several freeze tests switch the *real* ``repos/micropython`` (and
``micropython-lib``) checkout to different versions via ``switch()``. The autouse
fixture below captures each repo's checkout before a test and restores it
afterwards, so running these tests never leaves the developer's repos on another
branch/tag (which previously left the repo on ``master`` / preview).
"""

import subprocess
from pathlib import Path

import pytest


def _current_git_ref(repo: str) -> str:
    """Return the current branch name, or the commit sha if HEAD is detached."""
    branch = subprocess.run(
        ["git", "-C", repo, "symbolic-ref", "--short", "-q", "HEAD"],
        capture_output=True,
        text=True,
    ).stdout.strip()
    if branch:
        return branch
    return subprocess.run(
        ["git", "-C", repo, "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    ).stdout.strip()


@pytest.fixture(autouse=True)
def _restore_micropython_checkout(testrepo_micropython: Path, testrepo_micropython_lib: Path):
    """Capture and restore the micropython (+lib) repo checkouts around each test.

    Runs on teardown even if the test fails, so a switched repo is always restored.
    """
    repos = [testrepo_micropython.as_posix(), testrepo_micropython_lib.as_posix()]
    originals = {r: _current_git_ref(r) for r in repos}
    try:
        yield
    finally:
        for repo, ref in originals.items():
            if ref:
                subprocess.run(
                    ["git", "-C", repo, "checkout", "--quiet", ref],
                    capture_output=True,
                    text=True,
                )
