"simple Git module, where needed via powershell "
import subprocess
import os

def scriptpath(script: str):
    "get path where the powershell helper script is located"
    try:
        _scriptpath = os.path.dirname(os.path.realpath(__file__))
    except OSError:
        _scriptpath = "./src"
    return os.path.join(_scriptpath, script)

def get_tag(repo: str = None) -> str:
    """
    get the most recent git version tag of a local repo"
    repo should be in the form of : path/.git
        ../micropython/.git
    returns the tag or None
    """
    if not repo:
        repo = './.git'
    elif not repo.endswith('.git'):
        repo += '/.git'

    cmd = ['git', '--git-dir='+ repo, 'describe']
    result = _run_git(cmd, expect_stderr=True)
    if not result:
        return None
    tag: str = result.stdout.decode("utf-8")
    tag = tag.replace('\r', '').replace('\n', '')
    return tag


def _run_git(cmd: str, expect_stderr=False):
    "run a external (git) command and deal with some of the errors"
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        if result.stderr != b'':
            if not expect_stderr:
                raise Exception(result.stderr.decode("utf-8"))
            print(result.stderr.decode("utf-8"))

    except subprocess.CalledProcessError as err:
        # raise exception?
        raise Exception(err)
        # print(err)
        # return None

    if result.returncode < 0:
        raise Exception(result.stderr.decode("utf-8"))
    return result

def checkout_tag(tag: str, repo: str = None) -> bool:
    """
    get the most recent git version tag of a local repo"
    repo should be in the form of : path/.git
        ../micropython/.git
    returns the tag or None
    """
    if not repo:
        repo = '.'
    elif repo.endswith('.git'):
        repo = os.path.basename(repo)

    cmd = ["pwsh", scriptpath('git-checkout-tag.ps1'), '-repo', repo, '-tag', tag]
    result = _run_git(cmd, expect_stderr=True)
    if not result:
        return False
    # actually a good result
    print(result.stderr.decode("utf-8"))
    return True
    

    # todo: retry without powershell
    # cmd = ['git', 'checkout', 'tags/'+ tag]
    # try:
    #     result = subprocess.run(cmd, capture_output=True, check=True, cwd='../micropython')
    #     if result.stderr != b'':
    #         print(result.stderr.decode("utf-8"))
    #         return False
    #     print(result.stdout)
    #     return True
    # except  subprocess.CalledProcessError as e:
    #     print("Error: ", e.returncode, e.stderr)
    #     return False


def fetch(repo: str = None) -> bool:
    """
    fetches a repo
    repo should be in the form of : path/.git
        ../micropython/.git
    returns True on success
    """
    if not repo:
        repo = './.git'
    elif not repo.endswith('.git'):
        repo += '/.git'

    cmd = ['git', '--git-dir='+ repo, 'fetch origin']
    result = _run_git(cmd)
    if not result:
        return False
    return result.returncode == 0

def pull(repo: str = None, branch='master') -> bool:
    """
    pull a repo origin into master
    repo should be in the form of : path/.git
        ../micropython/.git
    returns True on success
    """
    if not repo:
        repo = './.git'
    elif not repo.endswith('.git'):
        repo += '/.git'

    # first checkout HEAD
    cmd = ['git', '--git-dir='+ repo, 'reset', '--hard', 'head', '-q']
    result = _run_git(cmd, expect_stderr=True)
    if not result:
        print("error durign git checkout heade", result)
        return False

    cmd = ['git', '--git-dir='+ repo, 'pull', 'origin', branch, '-q']
    result = _run_git(cmd, expect_stderr=True)
    if not result:
        print("error durign pull", result)
        return False
    return result.returncode == 0

