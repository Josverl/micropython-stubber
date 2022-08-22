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
    else:
        mpy_path = CONFIG.mpy_path
        mpy_lib_path = CONFIG.mpy_lib_path

    # if exist : fetch
    # allow switch to different tag

    if not (mpy_path / ".git").exists():
        git.clone(remote_repo="https://github.com/micropython/micropython.git", path=mpy_path)
    else:
        git.fetch(mpy_path)
        git.pull(mpy_path)

    if not (mpy_lib_path / ".git").exists():
        git.clone(remote_repo="https://github.com/micropython/micropython-lib.git", path=mpy_lib_path)
    else:
        git.fetch(mpy_lib_path)
    click.echo(f"{mpy_lib_path} {git.get_tag(mpy_path)}")
    click.echo(f"{mpy_lib_path} {git.get_tag(mpy_lib_path)}")
