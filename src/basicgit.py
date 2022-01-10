"""
simple Git module, where needed via powershell
"""
from typing import Union
import subprocess
import os
from typing import Union, List


def _run_git(cmd: List[str], repo: str = None, expect_stderr=False):
    "run a external (git) command in the repo's folder and deal with some of the errors"
    try:
        if repo:
            repo = repo.replace("\\", "/")
            result = subprocess.run(cmd, capture_output=True, check=True, cwd=os.path.abspath(repo))
        else:
            result = subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        # add some logging for github actions
        print("Exception on process, rc=", e.returncode, "output=", e.output)
        if e.returncode == 128:
            pwd = os.system("pwd")
            print(f"current directory: {pwd}")
            if repo:
                cwd = os.path.abspath(repo)
                print(f"git directory: {cwd}")
        return ""
    if result.stderr != b"":
        if not expect_stderr:
            raise Exception(result.stderr.decode("utf-8"))
        print(result.stderr.decode("utf-8"))

    if result.returncode < 0:
        raise Exception(result.stderr.decode("utf-8"))
    return result


def get_tag(repo: str = None, abbreviate: bool = True) -> Union[str, None]:
    """
    get the most recent git version tag of a local repo
    repo should be in the form of : repo = "./micropython"

    returns the tag or None
    """
    if not repo:
        repo = "."
    repo = repo.replace("\\", "/")

    result = _run_git(["git", "describe"], repo=repo, expect_stderr=True)
    if not result:
        return None
    tag: str = result.stdout.decode("utf-8")
    tag = tag.replace("\r", "").replace("\n", "")
    if abbreviate and "-" in tag:
        # this may or not be the latest on the main branch
        result = _run_git(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo=repo, expect_stderr=True)
        if result:
            ref: str = result.stdout.decode("utf-8").replace("\r", "").replace("\n", "")
            if ref in ["main", "master"]:
                tag = "latest"
            elif ref in ["fix_lib_documentation"]:
                tag = ref
    return tag


def checkout_tag(tag: str, repo: str = None) -> bool:
    """
    checkout a specific git tag
    """
    cmd = ["git", "checkout", "tags/" + tag, "--quiet", "--force"]
    result = _run_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        return False
    # actually a good result
    print(result.stderr.decode("utf-8"))
    return True


def checkout_commit(commit_hash: str, repo: str = None) -> bool:
    """
    Checkout a specific commit
    """
    cmd = ["git", "checkout", commit_hash, "--quiet", "--force"]
    result = _run_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        return False
    # actually a good result
    print(result.stderr.decode("utf-8"))
    return True


def switch_tag(tag: str, repo: str = None) -> bool:
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
    print(result.stderr.decode("utf-8"))
    return True


def switch_branch(branch: str, repo: str = None) -> bool:
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
    print(result.stderr.decode("utf-8"))
    return True


def fetch(repo: str) -> bool:
    """
    fetches a repo
    repo should be in the form of : path/.git
    repo = '../micropython/.git'
    returns True on success
    """
    if not repo:
        raise NotADirectoryError
    repo = repo.replace("\\", "/")
    cmd = ["git", "fetch origin"]
    result = _run_git(cmd, repo=repo)
    if not result:
        return False
    return result.returncode == 0


def pull(repo: str, branch="main") -> bool:
    """
    pull a repo origin into main
    repo should be in the form of : path/.git
    repo = '../micropython/.git'
    returns True on success
    """
    if not repo:
        raise NotADirectoryError
    repo = repo.replace("\\", "/")
    # first checkout HEAD
    cmd = ["git", "checkout", "main", "--quiet", "--force"]
    result = _run_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        print("error during git checkout main", result)
        return False

    cmd = ["git", "pull", "origin", branch, "--quiet"]
    result = _run_git(cmd, repo=repo, expect_stderr=True)
    if not result:
        print("error durign pull", result)
        return False
    return result.returncode == 0
