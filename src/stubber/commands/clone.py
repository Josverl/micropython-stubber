##########################################################################################
# clone
##########################################################################################
import logging
import os
from pathlib import Path
from typing import Union

import click
import stubber.basicgit as git
from stubber.utils.config import CONFIG
from stubber.utils.my_version import __version__

from .stubber_cli import stubber_cli

##########################################################################################
log = logging.getLogger("stubber")
#########################################################################################


@stubber_cli.command(name="clone")
@click.option("--path", "-p", default=CONFIG.repo_path.as_posix(), type=click.Path(file_okay=False, dir_okay=True))
def cli_clone(path: Union[str, Path]):
    """
    Clone/fetch the micropython repos locally.

    The local repos are used to generate frozen-stubs and doc-stubs.
    """
    dest_path = Path(path)
    if not dest_path.exists():
        os.mkdir(dest_path)
    # repos are relative to provided path
    if dest_path != CONFIG.repo_path:
        mpy_path = dest_path / "micropython"
        mpy_lib_path = dest_path / "micropython-lib"
        # mpy_stubs_path = dest_path / "micropython-stubs"
    else:
        mpy_path = CONFIG.mpy_path
        mpy_lib_path = CONFIG.mpy_lib_path
        # mpy_stubs_path = CONFIG.mpy_stubs_path

    repos = [
        (mpy_path, "https://github.com/micropython/micropython.git", "master"),
        (mpy_lib_path, "https://github.com/micropython/micropython-lib.git", "master"),
        # (mpy_stubs_path, "https://github.com/josverl/micropython-stubs.git", "main"),
    ]

    for _path, remote, branch in repos:
        if not (_path / ".git").exists():
            log.info(f"Cloning {_path.name}...")
            git.clone(remote_repo=remote, path=_path)
        else:
            log.info(f"{_path.name} already exists, fetching...")
            git.fetch(
                _path,
            )
            git.pull(_path, branch=branch)  # DEFAULT

    click.echo(f"{mpy_lib_path} {git.get_tag(mpy_path)}")
    click.echo(f"{mpy_lib_path} {git.get_tag(mpy_lib_path)}")
