"""
Code from micropyton project and adapted to use the same versioning scheme
"""

from __future__ import print_function

import subprocess
from pathlib import Path

from packaging.version import parse


def get_version_info_from_git(path: Path = Path.cwd()):
    """return the version info from the git repository specified.
    returns: a 2-tuple containing git_tag, short_hash

    """
    # Python 2.6 doesn't have check_output, so check for that
    try:
        subprocess.check_output
        subprocess.check_call
    except AttributeError:  # pragma: no cover
        return None

    # Note: git describe doesn't work if no tag is available
    try:
        git_tag = subprocess.check_output(
            ["git", "describe", "--tags", "--dirty", "--always", "--match", "v[1-9].*"],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=path,
        ).strip()
    except subprocess.CalledProcessError as er:  # pragma: no cover
        if er.returncode == 128:
            # git exit code of 128 means no repository found
            return None
        git_tag = ""
    except OSError:
        return None
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        ).strip()
    except subprocess.CalledProcessError:  # pragma: no cover
        git_hash = "unknown"
    except OSError:
        return None

    try:
        # Check if there are any modified files.
        subprocess.check_call(["git", "diff", "--no-ext-diff", "--quiet", "--exit-code"], stderr=subprocess.STDOUT)
        # Check if there are any staged files.
        subprocess.check_call(["git", "diff-index", "--cached", "--quiet", "HEAD", "--"], stderr=subprocess.STDOUT)  # pragma: no cover
    except subprocess.CalledProcessError:
        git_hash += "-dirty"
    except OSError:
        return None

    return git_tag, git_hash


def get_version_build_from_git(path: Path = Path.cwd()):
    git_tag, short_hash = get_version_info_from_git(path)  # type: ignore
    assert git_tag is not None
    parts = git_tag.split("-")
    assert len(parts) >= 2
    ver = parse(parts[0])
    return ver, parts[1]


# def get_version_info_from_docs_conf():
#     with open(os.path.join(os.path.dirname(sys.argv[0]), "..", "docs", "conf.py")) as f:
#         for line in f:
#             if line.startswith("version = release = '"):
#                 ver = line.strip().split(" = ")[2].strip("'")
#                 git_tag = "v" + ver
#                 return git_tag, "<no hash>"
#     return None
