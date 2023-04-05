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
from typing import List, Tuple, Union
from loguru import logger as log
from pathlib import Path
import subprocess
import time
import serial.tools.list_ports
import subprocess

from threading import Timer

OK = 0
ERROR = -1


###############################################################################################


def run(cmd: List[str], timeout: int = 60, no_error=False) -> Tuple[int, List[str]]:
    """ "Run a command and return the output and return code as a tuple"""
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
        if proc.stdout:
            for line in proc.stdout:
                line = line.replace("\x1b[1A", "")  # remove cursor up
                output.append(line)
                if "Traceback " in line or "Error: " in line:
                    log.error(line.rstrip("\n"))
                else:
                    log.info(line.rstrip("\n"))  # remove newline
        if proc.stderr and not no_error:
            for line in proc.stderr:
                log.warning(line.rstrip("\n"))
    finally:
        timer.cancel()

    proc.wait(timeout=1)
    return proc.returncode, output


###############################################################################################
class MPRemoteBoard:
    """Class to run mpremote commands"""

    def __init__(self, port: str = ""):
        self.port = port

    @staticmethod
    def connected_boards():
        """Get a list of connected boards"""
        devices = [p.device for p in serial.tools.list_ports.comports()]
        return sorted(devices)

    def connect(self, port: str = "") -> bool:
        """Connect to a board"""
        if port:
            self.port = port
        log.info(f"Connecting to {self.port}")
        return self.run_command(["connect", self.port])[0] == OK

    def disconnect(self) -> bool:
        """Disconnect from a board"""
        if not self.port:
            log.error("No port connected")
            return False
        log.info(f"Disconnecting from {self.port}")
        return self.run_command(["disconnect"])[0] == OK

    def run_command(self, cmd: Union[str, List[str]], *, no_error: bool = False, timeout: int = 60):
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
        # TODO: ADD RESUME to keep state between commands
        if self.port:
            cmd = ["mpremote", "connect", self.port] + cmd
        else:
            # cmd = ["mpremote", "resume"] + cmd
            cmd = ["mpremote"] + cmd

        log.debug(" ".join(cmd))
        return run(cmd, timeout, no_error)

    def mip_install(self, name: str) -> bool:
        """Install a micropython package"""
        # install createstubs to the board
        cmd = ["mip", "install", name]
        return self.run_command(cmd)[0] == OK


def copy_createstubs(board: MPRemoteBoard) -> bool:
    """Copy createstubs to the board"""
    # copy createstubs.py to the destination folder
    do = [
        ["exec", "import os;os.mkdir('lib') if not ('lib' in os.listdir()) else print('folder lib already exists')"],
        "cp ./src/stubber/board/createstubs_mem.py :lib/createstubs_mem.py",
        "cp ./src/stubber/board/createstubs_db.py :lib/createstubs_db.py",
        "cp ./src/stubber/board/logging.py :lib/logging.py",
        # "cp ./src/stubber/board/modulelist.txt :lib/modulelist.txt",
        "cp ./scratch/modulelist.txt :lib/modulelist.txt",
    ]
    ok = True
    for cmd in do:
        rc, _ = board.run_command(cmd)
        if rc != OK:
            ok = False
    return ok


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
    if TESTING:
        ok = copy_createstubs(board)
        # ok = board.mip_install("github:josverl/micropython-stubber/mip/full.json@board_stubber")
    else:
        ok = board.mip_install("github:josverl/micropython-stubber")
    if not ok:
        return ERROR, []

    time.sleep(2)

    # TODO: run createstubs _db variant - until done
    cmd = ["mount", str(dest)] if dest else []
    cmd += ["exec", "import createstubs_mem"]

    rc, out = board.run_command(cmd, timeout=10 * 60)
    if rc != OK:
        return ERROR, []

    # TODO: post_processing(dest)

    return OK, out


TESTING = True


def main():
    # if not check_tools():
    #     log.warning("Some tools are missing. Please install them first.")
    #     install_tools()
    dest = Path("./scratch")

    for _ in range(3):
        for mpr_port in MPRemoteBoard.connected_boards():
            board = MPRemoteBoard(mpr_port)

            log.info(f"Generating stubs for {board.port}")
            # check if the board is accesible and responsive
            rc, _ = board.run_command(["exec", "import os;print(os.uname())"])
            rc, _ = board.run_command("exec help('modules')", no_error=True)

            if rc != OK:
                log.error(f"Failed to connect to {board.port}")
                continue
            rc, my_stubs = generate_board_stubs(dest, board)
            if rc == OK:
                log.success(f" ~~{len(my_stubs)} Stubs generated for {board.port}")
            else:
                log.error(f"Failed to generate stubs for {board.port}")


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
        format_str = "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module: <18}</cyan> - <level>{message}</level>"
    else:
        format_str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    log.add(sys.stderr, level=level, backtrace=True, diagnose=True, colorize=True, format=format_str)
    # log.info(f"micropython-stubber {__version__}")
    return level


if __name__ == "__main__":
    set_loglevel(0)
    main()

"WARN  :stubber :\x1b[1ASkip module: _mqtt                     Module not found.                                                              \n"
