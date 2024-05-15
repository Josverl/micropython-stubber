"""
Code from micropyton project and adapted to use the same versioning scheme
"""

from __future__ import print_function

import subprocess
from pathlib import Path
from typing import Optional, Tuple, Union


def get_version_info_from_git(path: Optional[Path] = None) -> Tuple[Union[str, None], Union[str, None]]:
    """return the version info from the git repository specified.
    returns: a 2-tuple containing git_tag, short_hash

    """
    path = path or Path.cwd()
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
            return (None, None)
        git_tag = ""
    except OSError:
        return (None, None)
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        ).strip()
    except subprocess.CalledProcessError:  # pragma: no cover
        git_hash = "unknown"
    except OSError:
        return (None, None)

    try:
        # Check if there are any modified files.
        subprocess.check_call(["git", "diff", "--no-ext-diff", "--quiet", "--exit-code"], stderr=subprocess.STDOUT)
        # Check if there are any staged files.
        subprocess.check_call(["git", "diff-index", "--cached", "--quiet", "HEAD", "--"], stderr=subprocess.STDOUT)  # pragma: no cover
    except subprocess.CalledProcessError:
        git_hash += "-dirty"
    except OSError:
        return (None, None)

    return git_tag, git_hash
