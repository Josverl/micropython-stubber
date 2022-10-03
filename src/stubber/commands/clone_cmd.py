##########################################################################################
# clone
##########################################################################################
import os
from pathlib import Path
from typing import List, Tuple, Union

import click
import stubber.basicgit as git
from loguru import logger as log
from stubber.utils.config import CONFIG

from .cli import stubber_cli

##########################################################################################
# log = logging.getLogger("stubber")
#########################################################################################


@stubber_cli.command(name="clone")
@click.option("--path", "-p", default=CONFIG.repo_path.as_posix(), type=click.Path(file_okay=False, dir_okay=True))
@click.option("--add-stubs/--no-stubs", "stubs", default=False, is_flag=True, help="Also clone the micropython-stubs repo")
def cli_clone(path: Union[str, Path], stubs: bool = False):
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
        mpy_stubs_path = dest_path / "micropython-stubs"
    else:
        mpy_path = CONFIG.mpy_path
        mpy_lib_path = CONFIG.mpy_lib_path

        mpy_stubs_path = CONFIG.stub_path.parent

    repos: List[Tuple[Path, str, str]] = [
        (mpy_path, "https://github.com/micropython/micropython.git", "master"),
        (mpy_lib_path, "https://github.com/micropython/micropython-lib.git", "master"),
    ]
    if stubs:
        repos.append((mpy_stubs_path, "https://github.com/josverl/micropython-stubs.git", "main"))

    for _path, remote, branch in repos:
        log.info(f"Cloning {remote} branch {branch} to {_path}")
        if not (_path / ".git").exists():
            log.debug(f"Cloning {_path.name}...")
            git.clone(remote_repo=remote, path=_path)
        else:
            log.debug(f"{_path.name} already exists, fetching...")
            git.fetch(
                _path,
            )
            git.pull(_path, branch=branch)  # DEFAULT

    log.info(f"{mpy_path} {git.get_tag(mpy_path)}")
    log.info(f"{mpy_lib_path} {git.get_tag(mpy_lib_path)}")
    # click.echo(f"{mpy_stubs_path} {git.get_tag(mpy_stubs_path)}")
