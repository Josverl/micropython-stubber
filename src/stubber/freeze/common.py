import re
import shutil
from pathlib import Path
from typing import Tuple

from loguru import logger as log


def get_portboard(manifest_path: Path):
    """
    returns a 2-tuple of the port and board in the provided manifest path

    raises an ValueError if neither a port or board can be found
    """
    # https://regex101.com/r/tv7JX4/1
    re_pb = r".*micropython[\/\\]ports[\/\\](?P<port>[\w_-]*)([\/\\]boards[\/\\](?P<board>\w*))?[\/\\]"
    mpy_port = mpy_board = ""
    matches = re.search(re_pb, manifest_path.absolute().as_posix())
    if matches:
        # port and board
        mpy_port = str(matches.group("port") or "")
        mpy_board = str(matches.group("board") or "")
        return mpy_port, mpy_board
    log.error(f"no port or board found in {manifest_path}")
    raise (ValueError("Neither port or board found in path"))


def get_freeze_path(stub_path: Path, port: str, board: str) -> Tuple[Path, str]:
    """
    get path to a folder to store the frozen stubs for the given port/board
    """
    if port == "":
        raise ValueError("port must be provided")

    if board == "":
        board = "GENERIC"

    if board == "manifest_release":
        board = "RELEASE"
    # set global for later use - must be an absolute path.
    freeze_path = (stub_path / port / board).absolute()
    return freeze_path, board


def apply_frozen_module_fixes(freeze_path: Path, mpy_path: Path):
    """
    apply common fixes to the fozen modules to improve stub generation
    """
    # NOTE: FIX 1 add __init__.py to umqtt
    if (freeze_path / "umqtt/robust.py").exists():  # and not (freeze_path / "umqtt" / "__init__.py").exists():
        log.debug(f"add missing : umqtt/__init__.py")
        with open(freeze_path / "umqtt" / "__init__.py", "a") as f:
            f.write("")

    # NOTE: FIX 2 compensate for expicitly omited task.py from freeze manifest
    # this is normally implemented as a C module, let's use the .py version to generate a stub for this
    if (freeze_path / "uasyncio").exists() and not (freeze_path / "uasyncio" / "task.py").exists():
        # copy task.py from micropython\extmod\uasyncio\task.py to stub_folder
        log.debug(f"add missing : uasyncio/task.py")
        task_py = mpy_path / "extmod" / "uasyncio" / "task.py"
        try:
            shutil.copy(str(task_py), str(freeze_path / "uasyncio"))
        except OSError as er:
            log.warning(f"error copying {task_py} : {er}")
            # try to continue
