"""
switch to a specific version of the micropython repos
"""

from pathlib import Path
from typing import Optional, Union

import click
import stubber.basicgit as git
from stubber.utils.config import CONFIG
from stubber.utils.repos import fetch_repos, repo_paths

from .cli import stubber_cli

##########################################################################################
# log = logging.getLogger("stubber")
#########################################################################################


# get version list from Git tags in the repo that is provided on the command line
try:
    VERSION_LIST = git.get_tags(CONFIG.mpy_path, minver="v1.10") + ["v1.9.3", "v1.9.4", "latest"]
except Exception:
    VERSION_LIST = ["latest"]  # type: ignore


@stubber_cli.command(name="switch")
@click.argument("tag", required=False, type=click.Choice(VERSION_LIST, case_sensitive=False))
@click.option("--path", "-p", default=CONFIG.repo_path.as_posix(), type=click.Path(file_okay=False, dir_okay=True))
def cli_switch(path: Union[str, Path], tag: Optional[str] = None):
    """
    Switch to a specific version of the micropython repos.

    The Micropython-lib repo will be checked out to a commit that corresponds
    in time to that version tag, in order to allow non-current versions to be
    stubbed correctly.

    The repros must be cloned already
    """

    try:
        mpy_path, mpy_lib_path = repo_paths(Path(path))
    except Exception:
        return -1
    if not tag:
        tag = "latest"
    result = fetch_repos(tag, mpy_path, mpy_lib_path)
    return -1 if result else 0
