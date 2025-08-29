""" utility functions to handle to cloned repos needed for stubbing."""

import csv
import os
import pkgutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Tuple, Union

import mpflash.basicgit as git
from mpflash.logger import log
from mpflash.versions import SET_PREVIEW, V_PREVIEW, get_stable_mp_version
from packaging.version import Version

from stubber.utils.config import CONFIG

# # log = logging.getLogger(__name__)


def switch(tag: str, *, mpy_path: Path, mpy_lib_path: Path):
    """
    Switch to a specific version of the micropython repos.

    Specify the version with --tag or --version to specify the version tag
    of the MicroPython repo.
    The Micropython-lib repo will be checked out to a commit that corresponds
    in time to that version tag, in order to allow non-current versions to be
    stubbed correctly.

    The repros must be cloned already
    """
    # fetch then switch
    git.fetch(mpy_path)
    git.fetch(mpy_lib_path)

    if not tag or tag in {"master", ""}:
        tag = V_PREVIEW
    if tag in SET_PREVIEW:
        git.switch_branch(repo=mpy_path, branch="master")
    else:
        git.checkout_tag(repo=mpy_path, tag=tag)
    match_lib_with_mpy(version_tag=tag, mpy_path=mpy_path, lib_path=mpy_lib_path)


def read_micropython_lib_commits(filename: str = "data/micropython_tags.csv"):
    """
    Read a csv with the micropython version and matching micropython-lib commit-hashes
    these can be used to make sure that the correct micropython-lib version is checked out.

    filename is relative to the 'stubber' package

        git for-each-ref --sort=creatordate --format '%(refname) %(creatordate)' refs/tags
    """
    data = pkgutil.get_data("stubber", filename)
    if not data:
        raise FileNotFoundError(f"Resource {filename} not found")
    version_commit = defaultdict()
    with tempfile.NamedTemporaryFile(prefix="tags", suffix=".csv", mode="w+t") as ntf:
        ntf.file.write(data.decode(encoding="utf8"))
        ntf.file.seek(0)
        # read the csv file using DictReader
        reader = csv.DictReader(ntf.file, skipinitialspace=True)  # dialect="excel",
        rows = list(reader)
        # create a dict version --> commit_hash
        version_commit = {
            row["version"].split("/")[-1]: row["lib_commit_hash"]
            for row in rows
            if row["version"].startswith("refs/tags/")
        }
    # add default
    version_commit = defaultdict(lambda: "master", version_commit)
    return version_commit


def sync_submodules(repo: Union[Path, str]) -> bool:
    """
    make sure any submodules are in sync
    """
    cmds = [
        ["git", "submodule", "sync", "--quiet"],
        # ["git", "submodule", "update", "--quiet"],
        ["git", "submodule", "update", "--init", "lib/micropython-lib"],
    ]
    for cmd in cmds:
        if result := git._run_local_git(cmd, repo=repo, expect_stderr=True):
            # actually a good result
            log.debug(result.stderr)
        else:
            return False
    checkout_arduino_lib(Path(repo))
    return True


def checkout_arduino_lib(mpy_path: Path):
    """
    Checkout the arduino-lib submodule repo if it exists

    This is needed as some of the arduino boards freeze modules originationg from the arduino-lib
    """
    # arduino_lib_path = mpy_path / "lib/arduino-lib"
    if (mpy_path / "lib/arduino-lib").exists():
        cmd = ["git", "submodule", "update", "--init", "lib/arduino-lib"]
        try:
            result = subprocess.run(cmd, cwd=mpy_path, check=True)
            log.info(f"checkout arduino-lib: {result.returncode}")
        except subprocess.CalledProcessError as e:
            log.warning("Could not check out arduino-lib, error: ", e)


def match_lib_with_mpy(version_tag: str, mpy_path: Path, lib_path: Path) -> bool:
    micropython_lib_commits = read_micropython_lib_commits()
    # Make sure that the correct micropython-lib release is checked out
    #  check if micropython-lib has matching tags
    if version_tag in SET_PREVIEW:
        # micropython-lib is now a submodule
        result = git.checkout_commit("master", lib_path)
        if not result:
            log.error("Could not checkout micropython-lib @master")
            return False

        return sync_submodules(mpy_path)
    elif Version(version_tag) >= Version("v1.20.0"):
        # micropython-lib is now a submodule
        result = git.checkout_tag(version_tag, lib_path)
        if not result:
            log.warning(f"Could not checkout micropython-lib @{version_tag}")
            if not git.checkout_tag("master", lib_path):
                log.error("Could not checkout micropython-lib @master")
                return False
        return sync_submodules(mpy_path)
    else:
        log.info(
            f"Matching repo's:  Micropython {version_tag} needs micropython-lib:{micropython_lib_commits[version_tag]}"
        )
        return git.checkout_commit(micropython_lib_commits[version_tag], lib_path)


def fetch_repos(tag: str, mpy_path: Path, mpy_lib_path: Path):
    """Fetch updates, then switch to the provided tag/branch/commit"""
    log.info("fetch updates")
    git.fetch(mpy_path)
    git.fetch(mpy_lib_path)
    try:
        git.fetch(CONFIG.mpy_stubs_path)
    except Exception:
        log.trace("no stubs repo found : {CONFIG.mpy_stubs_path}")

    if not tag:
        tag = V_PREVIEW

    log.info(f"Switching to {tag}")
    
    # Handle special cases
    if tag == V_PREVIEW or tag in SET_PREVIEW:
        git.switch_branch(repo=mpy_path, branch="master")
    elif tag == "stable":
        tag = get_stable_mp_version()
        git.switch_tag(tag, repo=mpy_path)
    else:
        # Try to determine if this is a tag, branch, or commit
        # First try as a tag
        try:
            git.switch_tag(tag, repo=mpy_path)
        except:
            # If that fails, try as a branch
            try:
                git.switch_branch(repo=mpy_path, branch=tag)
            except:
                # If that fails, try as a commit hash
                try:
                    git.checkout_commit(tag, repo=mpy_path)
                except:
                    log.error(f"Could not switch to {tag} - not a valid tag, branch, or commit")
                    return False
    
    result = match_lib_with_mpy(version_tag=tag, mpy_path=mpy_path, lib_path=mpy_lib_path)

    log.info(f"{str(mpy_path):<40} {git.get_local_tag(mpy_path)}")
    log.info(f"{str(mpy_lib_path):<40} {git.get_local_tag(mpy_lib_path)}")
    try:
        sub_mod_path = mpy_path / "lib/micropython-lib"
        if (sub_mod_path / ".git").exists():
            log.info(f"{str(sub_mod_path):<40} {git.get_local_tag(sub_mod_path)}")
    except Exception:
        pass
    return result


def repo_paths(dest_path: Path) -> Tuple[Path, Path]:
    """Return the paths to the micropython and micropython-lib repos, given a path to the repos.'"""
    if not dest_path.exists():
        os.mkdir(dest_path)
    # repos are relative to provided path
    if dest_path != CONFIG.repo_path:
        mpy_path = dest_path / "micropython"
        mpy_lib_path = dest_path / "micropython-lib"
    else:
        mpy_path = CONFIG.mpy_path
        mpy_lib_path = CONFIG.mpy_lib_path

    # if no repos then error
    if not (mpy_path / ".git").exists():
        log.error(f"micropython repo not found at {mpy_path}")
        log.error("Run 'stubber clone' first to clone the required repositories")
        raise LookupError
    if not (mpy_lib_path / ".git").exists():
        log.error(f"micropython-lib repo not found at {mpy_lib_path}")
        log.error("Run 'stubber clone' first to clone the required repositories")
        raise LookupError
    return mpy_path, mpy_lib_path
