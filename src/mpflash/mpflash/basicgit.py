"""
Simple Git module, where needed via powershell

Some of the functions are based on the PyGithub module
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Union

import cachetools.func
from github import Auth, Github
from loguru import logger as log
from packaging.version import parse

# from mpflash.versions import SET_PREVIEW

# Token with no permissions to avoid throttling
# https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#getting-a-higher-rate-limit
PAT_NO_ACCESS = "github_pat" + "_11AAHPVFQ0qAkDnSUaMKSp" + "_ZkDl5NRRwBsUN6EYg9ahp1Dvj4FDDONnXVgimxC2EtpY7Q7BUKBoQ0Jq72X"
PAT = os.environ.get("GITHUB_TOKEN") or PAT_NO_ACCESS
GH_CLIENT = Github(auth=Auth.Token(PAT))


def _run_local_git(
    cmd: List[str],
    repo: Optional[Union[Path, str]] = None,
    expect_stderr=False,
    capture_output=True,
    echo_output=True,
):
    "run a external (git) command in the repo's folder and deal with some of the errors"
    try:
        if repo:
            if isinstance(repo, str):
                repo = Path(repo)
            result = subprocess.run(cmd, capture_output=capture_output, check=True, cwd=repo.absolute().as_posix(), encoding="utf-8")
        else:
            result = subprocess.run(cmd, capture_output=capture_output, check=True, encoding="utf-8")
    except (NotADirectoryError, FileNotFoundError) as e:  # pragma: no cover
        return None
    except subprocess.CalledProcessError as e:  # pragma: no cover
        # add some logging for github actions
        log.error(f"{str(e)} : { e.stderr}")
        return None
    if result.stderr and result.stderr != b"":
        stderr = result.stderr
        if "cloning into" in stderr.lower():
            # log.info(stderr)
            expect_stderr = True
        if "warning" in stderr.lower():
            log.warning(stderr)
            expect_stderr = True
        elif capture_output and echo_output:  # pragma: no cover
            log.info(stderr)
        if not expect_stderr:
            raise ChildProcessError(stderr)

    if result.returncode and result.returncode < 0:
        raise ChildProcessError(result.stderr)
    return result


def clone(remote_repo: str, path: Path, shallow: bool = False, tag: Optional[str] = None) -> bool:
    """git clone [--depth 1] [--branch <tag_name>] <remote> <directory>"""
    cmd = ["git", "clone"]
    if shallow:
        cmd += ["--depth", "1"]
    if tag in {"preview", "latest", "master"}:
        tag = None
    cmd += [remote_repo, "--branch", tag, str(path)] if tag else [remote_repo, str(path)]
    if result := _run_local_git(cmd, expect_stderr=True, capture_output=False):
        return result.returncode == 0
    else:
        return False


def get_local_tag(repo: Optional[Union[str, Path]] = None, abbreviate: bool = True) -> Union[str, None]:
    """
    get the most recent git version tag of a local repo
    repo Path should be in the form of : repo = "./repo/micropython"

    returns the tag or None
    """
    if not repo:
        repo = Path(".")
    elif isinstance(repo, str):
        repo = Path(repo)

    result = _run_local_git(
        # ["git", "describe", "--tags"],
        ["git", "describe", "--tags", "--dirty", "--always", "--match", "v[1-9].*"],
        repo=repo.as_posix(),
        expect_stderr=True,
    )
    if not result:
        return None
    tag: str = result.stdout
    tag = tag.replace("\r", "").replace("\n", "")
    if not abbreviate or "-" not in tag:
        return tag
    if "-preview" in tag:
        tag = tag.split("-preview")[0] + "-preview"
    return tag


def get_local_tags(repo: Optional[Path] = None, minver: Optional[str] = None) -> List[str]:
    """
    get list of all tags of a local repo
    """
    if not repo:
        repo = Path(".")

    result = _run_local_git(["git", "tag", "-l"], repo=repo.as_posix(), expect_stderr=True)
    if not result or result.returncode != 0:
        return []
    tags = result.stdout.replace("\r", "").split("\n")
    tags = [tag for tag in tags if tag.startswith("v")]
    if minver:
        tags = [tag for tag in tags if parse(tag) >= parse(minver)]
    return sorted(tags)


@cachetools.func.ttl_cache(maxsize=16, ttl=60)  # 60 seconds
def get_tags(repo: str, minver: Optional[str] = None) -> List[str]:
    """
    Get list of tag of a repote github repo
    """
    if not repo or not isinstance(repo, str) or "/" not in repo:  # type: ignore
        return []
    try:
        gh_repo = GH_CLIENT.get_repo(repo)
    except ConnectionError as e:
        # TODO: unable to capture the exeption
        log.warning(f"Unable to get tags - {e}")
        return []
    tags = [tag.name for tag in gh_repo.get_tags()]
    if minver:
        tags = [tag for tag in tags if parse(tag) >= parse(minver)]
    return sorted(tags)


def checkout_tag(tag: str, repo: Optional[Union[str, Path]] = None) -> bool:
    """
    checkout a specific git tag
    """
    cmd = ["git", "checkout", tag, "--quiet", "--force"]
    result = _run_local_git(cmd, repo=repo, expect_stderr=True, capture_output=True)
    if not result:
        return False
    # actually a good result
    msg = {result.stdout}
    if msg != {""}:
        log.warning(f"git message: {msg}")
    return True


def sync_submodules(repo: Optional[Union[Path, str]] = None) -> bool:
    """
    make sure any submodules are in sync
    """
    cmds = [
        ["git", "submodule", "sync", "--quiet"],
        # ["git", "submodule", "update", "--quiet"],
        ["git", "submodule", "update", "--init", "lib/micropython-lib"],
    ]
    for cmd in cmds:
        if result := _run_local_git(cmd, repo=repo, expect_stderr=True):
            # actually a good result
            log.debug(result.stderr)
        else:
            return False
    return True


def checkout_commit(commit_hash: str, repo: Optional[Union[Path, str]] = None) -> bool:
    """
    Checkout a specific commit
    """
    cmd = ["git", "checkout", commit_hash, "--quiet", "--force"]
    result = _run_local_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        return False
    # actually a good result
    log.debug(result.stderr)
    return True


def switch_tag(tag: Union[str, Path], repo: Optional[Union[Path, str]] = None) -> bool:
    """
    switch to the specified version tag of a local repo
    repo should be in the form of : path/.git
    repo = '../micropython/.git'
    returns None
    """

    cmd = ["git", "switch", "--detach", tag, "--quiet", "--force"]
    result = _run_local_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        return False
    # actually a good result
    log.debug(result.stderr)
    return True


def switch_branch(branch: str, repo: Optional[Union[Path, str]] = None) -> bool:
    """
    switch to the specified branch in a local repo"
    repo should be in the form of : path/.git
    repo = '../micropython/.git'
    returns None
    """
    cmd = ["git", "switch", branch, "--quiet", "--force"]
    result = _run_local_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        return False
    # actually a good result
    log.debug(result.stderr)
    return True


def fetch(repo: Union[Path, str]) -> bool:
    """
    fetches a repo
    repo should be in the form of : path/.git
    repo = '../micropython/.git'
    returns True on success
    """
    if not repo:
        raise NotADirectoryError

    cmd = ["git", "fetch", "--all", "--tags", "--quiet"]
    result = _run_local_git(cmd, repo=repo, echo_output=False)
    return result.returncode == 0 if result else False


def pull(repo: Union[Path, str], branch: str = "main") -> bool:
    """
    pull a repo origin into main
    repo should be in the form of : path/.git
    repo = '../micropython/.git'
    returns True on success
    """
    if not repo:
        raise NotADirectoryError
    repo = Path(repo)
    # first checkout HEAD
    cmd = ["git", "checkout", branch, "--quiet", "--force"]
    result = _run_local_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        log.error("error during git checkout main", result)
        return False

    cmd = ["git", "pull", "origin", branch, "--quiet", "--autostash"]
    result = _run_local_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        log.error("error durign pull", result)
        return False
    return result.returncode == 0


def get_git_describe(folder: Optional[str] = None):
    """
    Based on MicroPython makeversionhdr.py
    returns : current git tag, commits ,commit hash : "v1.19.1-841-g3446"
    """
    # Note: git describe doesn't work if no tag is available
    try:
        git_describe = subprocess.check_output(
            ["git", "describe", "--tags", "--dirty", "--always", "--match", "v[1-9].*"],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=folder,
        ).strip()
    except subprocess.CalledProcessError as er:
        if er.returncode == 128:
            # git exit code of 128 means no repository found
            return None
        git_describe = ""
    except OSError:
        return None
    # format
    return git_describe
