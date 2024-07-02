""" utility functions to handle to cloned repos needed for stubbing."""

import csv
import os
import pkgutil
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Tuple

from mpflash.logger import log
from packaging.version import Version

import mpflash.basicgit as git
from mpflash.versions import SET_PREVIEW, V_PREVIEW, get_stable_mp_version
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
    version_commit = defaultdict()  # lgtm [py/multiple-definition]
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

        return git.sync_submodules(mpy_path)
    elif Version(version_tag) >= Version("v1.20.0"):
        # micropython-lib is now a submodule
        result = git.checkout_tag(version_tag, lib_path)
        if not result:
            log.warning(f"Could not checkout micropython-lib @{version_tag}")
            if not git.checkout_tag("master", lib_path):
                log.error("Could not checkout micropython-lib @master")
                return False
        return git.sync_submodules(mpy_path)
    else:
        log.info(
            f"Matching repo's:  Micropython {version_tag} needs micropython-lib:{micropython_lib_commits[version_tag]}"
        )
        return git.checkout_commit(micropython_lib_commits[version_tag], lib_path)


def fetch_repos(tag: str, mpy_path: Path, mpy_lib_path: Path):
    """Fetch updates, then switch to the provided tag"""
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
    if tag == V_PREVIEW:
        git.switch_branch(repo=mpy_path, branch="master")
    else:
        if tag == "stable":
            tag = get_stable_mp_version()
        git.switch_tag(tag, repo=mpy_path)
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
        log.error("micropython repo not found")
        raise LookupError
    if not (mpy_lib_path / ".git").exists():
        log.error("micropython-lib repo not found")
        raise LookupError
    return mpy_path, mpy_lib_path
