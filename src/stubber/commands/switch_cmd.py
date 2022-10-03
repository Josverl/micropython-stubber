"""
switch 
"""

import os
from pathlib import Path
from typing import Optional, Union

import click
import stubber.basicgit as git
from loguru import logger as log
from stubber.utils.config import CONFIG
from stubber.utils.repos import match_lib_with_mpy

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
# WIP: Transition from Option to  Argument, currently supports both
@click.argument("tag", required=False, type=click.Choice(VERSION_LIST, case_sensitive=False))
@click.option("--path", "-p", default=CONFIG.repo_path.as_posix(), type=click.Path(file_okay=False, dir_okay=True))
def cli_switch(path: Union[str, Path], tag: Optional[str] = None):
    """
    Switch to a specific version of the micropython repos.

    Specify the version of the MicroPython repo.
    use of the --tag or --version is deprocated

    The Micropython-lib repo will be checked out to a commit that corresponds
    in time to that version tag, in order to allow non-current versions to be
    stubbed correctly.

    The repros must be cloned already
    """
    dest_path = Path(path)
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
        return -1
    if not (mpy_lib_path / ".git").exists():
        log.error("micropython-lib repo not found")
        return -1

    # fetch then switch
    log.info(f"fetch updates")
    git.fetch(mpy_path)
    git.fetch(mpy_lib_path)
    try:
        git.fetch(CONFIG.stub_path.parent)
    except Exception:
        log.trace("no stubs repo found : {CONFIG.stub_path.parent}")

    if not tag or tag == "":
        tag = "latest"

    log.info(f"Switching to {tag}")
    if tag == "latest":
        git.switch_branch(repo=mpy_path, branch="master")
    else:
        git.checkout_tag(repo=mpy_path, tag=tag)
    match_lib_with_mpy(version_tag=tag, lib_path=mpy_lib_path)

    log.info(f"{mpy_lib_path} {git.get_tag(mpy_path)}")
    log.info(f"{mpy_lib_path} {git.get_tag(mpy_lib_path)}")
    return 0
