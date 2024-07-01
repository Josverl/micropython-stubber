"""
switch to a specific version of the micropython repos
"""

from pathlib import Path
from typing import Optional, Union

import rich_click as click

import mpflash.basicgit as git
from stubber.utils.config import CONFIG
from stubber.utils.repos import fetch_repos, repo_paths
from mpflash.versions import SET_PREVIEW, V_PREVIEW

from .cli import stubber_cli

##########################################################################################
# log = logging.getLogger("stubber")
#########################################################################################


# get version list from Git tags in the repo that is provided on the command line

try:
    VERSION_LIST = git.get_tags("micropython/micropython", minver="v1.9.3") + [
        V_PREVIEW,
        "latest",
        "stable",
    ]
except Exception:
    # offline fallback
    VERSION_LIST = ["v1.91.1", "v1.20.1", "v1.21.0", "v1.22.1", "preview", "stable"]


@stubber_cli.command(name="switch")
@click.argument("tag", required=False, type=click.Choice(VERSION_LIST, case_sensitive=False))
@click.option(
    "--path",
    "-p",
    default=CONFIG.repo_path.as_posix(),
    type=click.Path(file_okay=False, dir_okay=True),
)
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
    if not tag or tag in SET_PREVIEW:
        tag = V_PREVIEW

    result = fetch_repos(tag, mpy_path, mpy_lib_path)
    return -1 if result else 0
