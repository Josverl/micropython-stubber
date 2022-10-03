"""
simple Git module, where needed via powershell
"""
import subprocess
from pathlib import Path
from typing import List, Optional, Union

from loguru import logger as log
from packaging.version import parse


def _run_git(
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
            result = subprocess.run(cmd, capture_output=capture_output, check=True, cwd=repo.absolute().as_posix())
        else:
            result = subprocess.run(cmd, capture_output=capture_output, check=True)
    except (NotADirectoryError, FileNotFoundError) as e:  # pragma: no cover
        return None
    except subprocess.CalledProcessError as e:  # pragma: no cover
        # add some logging for github actions
        log.error("Exception on process, rc=", e.returncode, "output=", e.output.decode("utf-8"), "\nstderr=", e.stderr.decode("utf-8"))
        return None
    if result.stderr and result.stderr != b"":
        stderr = result.stderr.decode("utf-8")
        if "warning" in stderr.lower():
            log.warning(stderr)
            expect_stderr = True
        elif capture_output and echo_output:  # pragma: no cover
            log.error(stderr)
        if not expect_stderr:
            raise Exception(stderr)

    if result.returncode < 0:
        raise Exception(result.stderr.decode("utf-8"))
    return result


def clone(remote_repo: str, path: Path, shallow=False, tag: Optional[str] = None) -> bool:
    "git clone [--depth 1] [--branch <tag_name>] <remote> <directory>"
    cmd = ["git", "clone"]
    if shallow:
        cmd += ["--depth", "1"]
    if tag in ("latest", "master"):
        tag = None
    if not tag:
        cmd += [remote_repo, str(path)]
    else:
        cmd += [remote_repo, "--branch", tag, str(path)]
    result = _run_git(cmd, expect_stderr=True, capture_output=False)
    if result:
        return result.returncode == 0
    else:
        return False


def get_tag(repo: Optional[Union[str, Path]] = None, abbreviate: bool = True) -> Union[str, None]:
    """
    get the most recent git version tag of a local repo
    repo Path should be in the form of : repo = "./repo/micropython"

    returns the tag or None
    """
    if not repo:
        repo = Path(".")
    elif isinstance(repo, str):
        repo = Path(repo)

    result = _run_git(["git", "describe"], repo=repo.as_posix(), expect_stderr=True)
    if not result:
        return None
    tag: str = result.stdout.decode("utf-8")
    tag = tag.replace("\r", "").replace("\n", "")
    if abbreviate and "-" in tag:
        # this may or not be the latest on the main branch
        # result = _run_git(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo=repo, expect_stderr=True)
        result = _run_git(["git", "status", "--branch"], repo=repo.as_posix(), expect_stderr=True)
        if result:
            lines = result.stdout.decode("utf-8").replace("\r", "").split("\n")
            if lines[0].startswith("On branch"):
                if lines[0].endswith("master"):
                    tag = "latest"
                elif lines[0].endswith("fix_lib_documentation"):
                    tag = "fix_lib_documentation"
    return tag


def get_tags(repo: Optional[Path] = None, minver: Optional[str] = None) -> List[str]:
    """
    get list of tag of a local repo
    """
    if not repo:
        repo = Path(".")

    result = _run_git(["git", "tag", "-l"], repo=repo.as_posix(), expect_stderr=True)
    if not result or result.returncode != 0:
        return []
    tags = result.stdout.decode("utf-8").replace("\r", "").split("\n")
    tags = [tag for tag in tags if tag.startswith("v")]
    if minver:
        tags = [tag for tag in tags if parse(tag) >= parse(minver)]
    return sorted(tags)


def checkout_tag(tag: str, repo: Optional[Union[str, Path]] = None) -> bool:
    """
    checkout a specific git tag
    """
    cmd = ["git", "checkout", "tags/" + tag, "--detach", "--quiet", "--force"]
    result = _run_git(cmd, repo=repo, expect_stderr=True, capture_output=True)
    if not result:
        return False
    # actually a good result
    log.debug(result.stderr.decode("utf-8"))
    log.debug(result.stdout.decode("utf-8"))
    return True


def synch_submodules(repo: Optional[Union[Path, str]] = None) -> bool:
    """
    make sure any submodules are in syncj
    """
    cmds = [
        ["git", "submodule", "sync", "--quiet"],
        ["git", "submodule", "update", "--quiet"],
    ]
    for cmd in cmds:
        result = _run_git(cmd, repo=repo, expect_stderr=True)
        if not result:
            return False
        # actually a good result
        log.debug(result.stderr.decode("utf-8"))
    return True


def checkout_commit(commit_hash: str, repo: Optional[Union[Path, str]] = None) -> bool:
    """
    Checkout a specific commit
    """
    cmd = ["git", "checkout", commit_hash, "--quiet", "--force"]
    result = _run_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        return False
    # actually a good result
    log.debug(result.stderr.decode("utf-8"))
    synch_submodules(repo)
    return True


def switch_tag(tag: str, repo: Optional[Union[Path, str]] = None) -> bool:
    """
    get the most recent git version tag of a local repo"
    repo should be in the form of : path/.git
    repo = '../micropython/.git'
    returns the tag or None
    """

    cmd = ["git", "switch", "--detach", tag, "--quiet", "--force"]
    result = _run_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        return False
    # actually a good result
    log.debug(result.stderr.decode("utf-8"))
    synch_submodules(repo)
    return True


def switch_branch(branch: str, repo: Optional[Union[Path, str]] = None) -> bool:
    """
    get the most recent git version tag of a local repo"
    repo should be in the form of : path/.git
    repo = '../micropython/.git'
    returns the tag or None
    """
    cmd = ["git", "switch", branch, "--quiet", "--force"]
    result = _run_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        return False
    # actually a good result
    log.debug(result.stderr.decode("utf-8"))
    synch_submodules(repo)
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
    result = _run_git(cmd, repo=repo, echo_output=False)
    if not result:
        return False
    return result.returncode == 0


def pull(repo: Union[Path, str], branch="main") -> bool:
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
    result = _run_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        log.error("error during git checkout main", result)
        return False

    cmd = ["git", "pull", "origin", branch, "--quiet", "--autostash"]
    result = _run_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        log.error("error durign pull", result)
        return False
    return result.returncode == 0
