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
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        if result.stderr != b'':
            print(result.stderr.decode("utf-8"))
            raise Exception(result.stderr.decode("utf-8"))
        tag: str = result.stdout.decode("utf-8")
        tag = tag.replace('\r', '').replace('\n', '')
        return tag
    except  subprocess.CalledProcessError as err:
        print("Error: ", err.returncode, err.stderr)
        raise Exception(err.stderr) from err

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
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        print(err)
        return False
    if result.returncode < 0:
        raise Exception(result.stderr.decode("utf-8"))
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
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        if result.stderr != b'':
            print(result.stderr.decode("utf-8"))
            raise Exception(result.stderr.decode("utf-8"))
        return True

    except  subprocess.CalledProcessError as err:
        print("Error: ", err.returncode, err.stderr)
        raise Exception(err.stderr) from err

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

    cmd = ['git', '--git-dir='+ repo, 'pull', 'origin', branch]
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        # if result.stderr != b'':
        #     print(result.stderr.decode("utf-8"))
        #     raise Exception(result.stderr.decode("utf-8"))
        return result.returncode == 0

    except  subprocess.CalledProcessError as err:
        print("Error: ", err.returncode, err.stderr)
        raise Exception(err.stderr) from err
