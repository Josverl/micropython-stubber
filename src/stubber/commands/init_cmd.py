"""Initialize a local micropython-stubs workspace."""

import os
from pathlib import Path
from typing import Union

import mpflash.basicgit as git
import rich_click as click
from mpflash.logger import log

from stubber.commands.cli import stubber_cli
from stubber.commands.clone_cmd import cli_clone
from stubber.utils.repos import fetch_repos, repo_paths


@stubber_cli.command(name="init")
@click.option(
    "--path",
    "-p",
    default=".",
    type=click.Path(file_okay=False, dir_okay=True),
    help="Path where micropython-stubs should be created (default: current directory)",
)
def cli_init(path: Union[str, Path] = "."):
    """
    Initialize a new workspace.

    This command:
    1. Clones micropython-stubs into ./micropython-stubs
    2. Runs clone to fetch micropython + micropython-lib into ./repos
    3. Runs switch stable in ./repos
    """

    base_path = Path(path).resolve()
    stubs_path = (base_path / "micropython-stubs").resolve()

    if stubs_path.exists():
        log.error(f"Path already exists: {stubs_path}")
        return -1

    log.info(f"Cloning micropython-stubs to {stubs_path}")
    try:
        git.clone(
            remote_repo="https://github.com/josverl/micropython-stubs.git",
            path=stubs_path,
        )
    except Exception as exc:
        log.error(f"Failed to clone micropython-stubs: {exc}")
        return -1

    original_cwd = Path.cwd()
    os.chdir(stubs_path)

    try:
        clone_result = cli_clone.main(args=["--path", "repos"], standalone_mode=False)
        if clone_result:
            log.error("Failed to clone micropython and micropython-lib")
            os.chdir(original_cwd)
            return -1

        try:
            mpy_path, mpy_lib_path = repo_paths(Path("repos"))
        except Exception as exc:
            log.error(f"Could not locate cloned repos: {exc}")
            os.chdir(original_cwd)
            return -1

        if not fetch_repos("stable", mpy_path, mpy_lib_path):
            log.error("Failed to switch to stable")
            os.chdir(original_cwd)
            return -1

        # Stand out
        log.success(f"Workspace ready at {stubs_path}")
        log.success(f"To start working, run:  cd {stubs_path}")
        return 0

    except Exception as exc:
        log.error(f"Init failed: {exc}")
        os.chdir(original_cwd)
        return -1
