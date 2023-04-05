""" 
This script creates stubs for a connectes micropython MCU board.

# MPRemote is not working properly with ESP32 boards :-( at least on Windows)
# this was fixed in the latest version of mpremote, not published yet on pypi
# May need to find a way to build & include this 
pip install git+https://github.com/micropython/micropython.git#subdirectory=tools/mpremote
Fails on timeouts and errors in pip install 

Workaround
pip install git+https://github.com/josverl/mpremote.git#subdirectory=tools/mpremote
"""

import sys
from typing import List, NamedTuple, Optional, Tuple, Union
from loguru import logger as log
from pathlib import Path
import subprocess
import time
import serial.tools.list_ports
import subprocess

from threading import Timer
from tenacity import retry, stop_after_attempt, wait_fixed

OK = 0
ERROR = -1


###############################################################################################


def run(
    cmd: List[str],
    timeout: int = 60,
    no_error: bool = False,
    no_info: bool = False,
    *,
    error_tags: Optional[List[str]] = None,
    warning_tags: Optional[List[str]] = None,
    success_tags: Optional[List[str]] = None,
) -> Tuple[int, List[str]]:
    # sourcery skip: raise-specific-error
    """
    Run a command and return the output and return code as a tuple
    Parameters
    ----------
    cmd : List[str]
        The command to run
    timeout : int, optional
        The timeout in seconds, by default 60
    no_error : bool, optional
        If True, don't log errors, by default False
    no_info : bool, optional
        If True, don't log info, by default False
    error_tags : Optional[List[str]], optional
        A list of strings to look for in the output to log as errors, by default None
    warning_tags : Optional[List[str]], optional
        A list of strings to look for in the output to log as warnings, by default None
    Returns
    -------
    Tuple[int, List[str]]
        The return code and the output as a list of strings
    """
    if not error_tags:
        error_tags = ["Traceback ", "Error: ", "Exception: ", "ERROR :", "CRIT  :"]
    if not warning_tags:
        warning_tags = ["WARN  :"]  # , "Module not found."
    if not success_tags:
        success_tags = ["Created stubs for", "Path: /remote"]

    replace_tags = ["\x1b[1A"]

    output = []
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except FileNotFoundError as e:
        raise Exception(f"Failed to start {cmd[0]}") from e

    def timed_out():
        proc.kill()
        log.warning(f"Command {cmd} timed out after {timeout} seconds")

    timer = Timer(timeout, timed_out)
    try:
        timer.start()
        # stdout has most of the output, assign log categories based on text tags
        if proc.stdout:
            for line in proc.stdout:
                if not line or not line.strip():
                    continue
                for tag in replace_tags:
                    line = line.replace(tag, "")
                output.append(line)  # full output, no trimming
                line = line.rstrip("\n")
                # if any of the error tags in the line
                if any(tag in line for tag in error_tags) and not no_error:
                    log.error(line)
                elif any(tag in line for tag in warning_tags):
                    log.warning(line)
                elif any(tag in line for tag in success_tags):
                    log.success(line)
                else:
                    if not no_info:
                        log.info(line)
        if proc.stderr and not no_error:
            for line in proc.stderr:
                log.warning(line)
    finally:
        timer.cancel()

    proc.wait(timeout=1)
    return proc.returncode, output


###############################################################################################

UName = NamedTuple("UName", sysname=str, nodename=str, release=str, version=str, machine=str)

RETRIES = 3


class MPRemoteBoard:
    """Class to run mpremote commands"""

    def __init__(self, port: str = ""):
        self.port = port
        self.uname = None
        self.connected = False

    @staticmethod
    def connected_boards():
        """Get a list of connected boards"""
        devices = [p.device for p in serial.tools.list_ports.comports()]
        return sorted(devices)

    @retry(stop=stop_after_attempt(RETRIES), wait=wait_fixed(1))
    def get_uname(self):
        rc, result = self.run_command(["exec", "import os;print(os.uname())"], no_info=True)
        s = result[0]
        if "sysname=" in s:
            self.uname = eval(f"UName{s}")
        else:
            self.uname = UName(*s[1:-1].split(", "))
        self.connected = True
        return rc, self.uname

    def disconnect(self) -> bool:
        """Disconnect from a board"""
        if not self.connected:
            return True
        if not self.port:
            log.error("No port connected")
            self.connected = False
            return False
        log.info(f"Disconnecting from {self.port}")
        result = self.run_command(["disconnect"])[0] == OK
        self.connected = False
        return result

    @retry(stop=stop_after_attempt(RETRIES), wait=wait_fixed(2))
    def run_command(
        self,
        cmd: Union[str, List[str]],
        *,
        no_error: bool = False,
        no_info: bool = False,
        timeout: int = 60,
        **kwargs,
    ):
        """Run mpremote with the given command
        Parameters
        ----------
        cmd : Union[str,List[str]]
            The command to run, either a string or a list of strings
        check : bool, optional
            If True, raise an exception if the command fails, by default False
        Returns
        -------
        bool
            True if the command succeeded, False otherwise
        """
        if isinstance(cmd, str):
            cmd = cmd.split(" ")
        prefix = ["mpremote", "connect", self.port] if self.port else ["mpremote"]
        # if connected add resume to keep state between commands
        if self.connected:
            prefix += ["resume"]
        cmd = prefix + cmd
        log.debug(" ".join(cmd))
        result = run(cmd, timeout, no_error, no_info, **kwargs)
        self.connected = True
        return result

    @retry(stop=stop_after_attempt(RETRIES), wait=wait_fixed(1))
    def mip_install(self, name: str) -> bool:
        """Install a micropython package"""
        # install createstubs to the board
        cmd = ["mip", "install", name]
        result = self.run_command(cmd)[0] == OK
        self.connected = True
        return result


def copy_createstubs(board: MPRemoteBoard) -> bool:
    """Copy createstubs to the board"""
    # copy createstubs.py to the destination folder
    _full = [
        ["exec", "import os;os.mkdir('lib') if not ('lib' in os.listdir()) else print('folder lib already exists')"],
        "cp ./src/stubber/board/createstubs_mem.py :lib/createstubs_mem.py",
        "cp ./src/stubber/board/createstubs_db.py :lib/createstubs_db.py",
        "cp ./src/stubber/board/logging.py :lib/logging.py",
    ]
    # copy createstubs*_min.py to the destination folder
    _min = [
        ["exec", "import os;os.mkdir('lib') if not ('lib' in os.listdir()) else print('folder lib already exists')"],
        "cp ./src/stubber/board/createstubs_mem_min.py :lib/createstubs_mem.py",
        "cp ./src/stubber/board/createstubs_db_min.py :lib/createstubs_db.py",
    ]
    # copy createstubs*_mpy.mpy to the destination folder
    _mpy = [
        ["exec", "import os;os.mkdir('lib') if not ('lib' in os.listdir()) else print('folder lib already exists')"],
        "rm :lib/createstubs_mem.py",
        "rm :lib/createstubs_db.py",
        "cp ./src/stubber/board/createstubs_mem_mpy.mpy :lib/createstubs_mem.mpy",
        "cp ./src/stubber/board/createstubs_db_mpy.mpy :lib/createstubs_db.mpy",
    ]

    do = _mpy + [
        "rm :modulelist.done",
        # "cp ./scratch/modulelist.txt :lib/modulelist.txt",  # reduced set for testing
        "cp ./src/stubber/board/modulelist.txt :lib/modulelist.txt",
    ]

    ok = True  # assume all ok, unless one is not ok
    for cmd in do:
        rc, _ = board.run_command(cmd, no_error=True)
        if rc != OK:
            ok = False
    return ok


@retry(stop=stop_after_attempt(10), wait=wait_fixed(2))
def run_createstubs(dest: Path, board: MPRemoteBoard, variant: str = "db"):
    """Run createstubs on the board"""
    cmd_path = ["exec", 'import sys;sys.path.append("/lib") if "/lib" not in sys.path else "/lib already in path"']
    board.run_command(cmd_path)

    cmd = ["mount", str(dest)] if dest else []
    # cmd += ["exec", "import createstubs_mem"]
    cmd += ["exec", "import createstubs_db"]
    rc, out = board.run_command(cmd, timeout=5 * 60)
    if rc != OK and variant == "db":
        # assume createstubs ran out of memory and try again
        raise MemoryError("Memory error, try again")
    return rc, out


def generate_board_stubs(dest: Path, board: MPRemoteBoard) -> Tuple[int, List[str]]:
    """
    Generate the board stubs.
    Parameters
    ----------
    dest : Path
        The destination folder for the stubs
    port : str
        The port the board is connected to
    """
    # HOST -> MCU : copy createstubs to board
    if TESTING:
        ok = copy_createstubs(board)
        # ok = board.mip_install("github:josverl/micropython-stubber/mip/full.json@board_stubber")
    else:
        ok = board.mip_install("github:josverl/micropython-stubber")
    if not ok and not TESTING:
        return ERROR, []
    # HOST: remove .done file
    (dest / "modulelist.done").unlink(missing_ok=True)

    # MCU: add lib to path
    rc, out = run_createstubs(dest, board)

    if rc != OK:
        return ERROR, []

    # TODO: post_processing(dest)

    return OK, out


TESTING = True


def main():
    # if not check_tools():
    #     log.warning("Some tools are missing. Please install them first.")
    #     install_tools()
    dest = Path("./scratch/stubgen_test")

    # scan boards and just work with the ones that reponded with understandable data
    connected_boards = scan_boards(True)

    # scan boards and generate stubs
    for board in connected_boards:
        log.info(f"Connecting to {board.port}")
        rc, my_stubs = generate_board_stubs(dest, board)
        if rc == OK:
            log.success(f" ~~{len(my_stubs)} Stubs generated for {board.port}")
        else:
            log.error(f"Failed to generate stubs for {board.port}")


def scan_boards(optimistic: bool = False) -> List[MPRemoteBoard]:
    """
    This function scans for boards and returns a list of MPRemoteBoard objects.
    :return: list of MPRemoteBoard objects
    """
    boards = []
    for mpr_port in MPRemoteBoard.connected_boards():
        board = MPRemoteBoard(mpr_port)
        log.info(f"Attempt to connect to: {board.port}")
        try:
            rc, uname = board.get_uname()
            log.success(f"Detected board {uname.machine} {uname.release}")
            boards.append(board)
        except Exception:
            log.error(f"Failed to get uname for {board.port}")
            if optimistic:
                boards.append(board)
            continue
    return boards


def set_loglevel(verbose: int) -> str:
    """Set log level based on verbose level
    Get the level from the verbose setting (0=INFO, 1=DEBUG, 2=TRACE)
    Set the format string, based on the level.
    Add the handler to the logger, with the level and format string.
    Return the level
    """
    log.remove()
    level = {0: "INFO", 1: "DEBUG", 2: "TRACE"}.get(verbose, "TRACE")
    if level == "INFO":
        format_str = "<green>{time:HH:mm:ss}</green>|<level>{level: <8}</level>|<cyan>{module: <20}</cyan> - <level>{message}</level>"
    else:
        format_str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>|<level>{level: <8}</level>|<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    log.add(sys.stderr, level=level, backtrace=True, diagnose=True, colorize=True, format=format_str)
    # log.info(f"micropython-stubber {__version__}")
    return level


if __name__ == "__main__":
    set_loglevel(2)
    main()
