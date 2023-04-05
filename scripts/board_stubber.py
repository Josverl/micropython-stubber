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


from typing import List, Tuple, Union
from loguru import logger as log
from pathlib import Path
import subprocess
import time
import serial.tools.list_ports
import subprocess

from threading import Timer


# def check_tools():
#     """Check if all tools are available"""
#     # stubber
#     # pipx
#     # mpremote
#     return True


# def install_tools():
#     """Install all required tools"""
#     pass


def run(cmd: List[str], timeout: int = 10, no_error=False) -> Tuple[List[str], int]:
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
                log.info(line.rstrip("\n"))
                output.append(line)
        if proc.stderr and not no_error:
            for line in proc.stderr:
                log.warning(line.rstrip("\n"))
    finally:
        timer.cancel()

    proc.wait(timeout=1)
    return output, proc.returncode


def run_mpremote(port: str, cmd: Union[str, List[str]], *, no_error: bool = False):  # sourcery skip: assign-if-exp
    """Run mpremote with the given command
    Parameters
    ----------
    port : str
        The port the board is connected to
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
    if port:
        cmd = ["mpremote", "connect", port] + cmd
    else:
        # cmd = ["mpremote", "resume"] + cmd
        cmd = ["mpremote"] + cmd

    log.info(" ".join(cmd))
    return run(cmd, timeout=3 * 60, no_error=no_error)


def mip_install(name: str, port: str = "") -> bool:
    """Install a micropython package"""
    # install createstubs to the board
    cmd = ["mip", "install", name]
    _, rc = run_mpremote(port, cmd)
    return rc == 0


def copy_createstubs(port: str) -> bool:
    """Copy createstubs to theboard"""
    # copy createstubs.py to the destination folder
    do = [
        "mkdir lib",
        "cp ./src/stubber/board/createstubs_mem.py :lib/createstubs_mem.py",
        "cp ./src/stubber/board/createstubs_db.py :lib/createstubs_db.py",
        "cp ./src/stubber/board/logging.py :lib/logging.py",
        "cp ./src/stubber/board/modulelist.txt :lib/modulelist.txt",
    ]
    ok = True
    for cmd in do:
        _, rc = run_mpremote(port, cmd, no_error=True)
        if rc != 0:
            ok = False
    return ok


def generate_board_stubs(dest: Path, port: str = "") -> Tuple[bool, List[str]]:
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
        ok = copy_createstubs(port)
        # ok = mip_install("github:josverl/micropython-stubber/mip/full.json@board_stubber", port)
    else:
        ok = mip_install("github:josverl/micropython-stubber", port)
    if not ok:
        return False, []

    time.sleep(2)
    # run createstubs _mem variant

    cmd = ["mount", str(dest)] if dest else []
    cmd += ["exec", "import createstubs_mem"]

    out, rc = run_mpremote(port, cmd)
    if rc != 0:
        return False, []
    # post_processing(dest)
    # TODO: read path and count stubs from output
    return True, [out[-1]]


def get_connected_boards():
    """Get a list of connected boards"""
    devices = [p.device for p in serial.tools.list_ports.comports()]
    return sorted(devices)


TESTING = True


def main():
    # if not check_tools():
    #     log.warning("Some tools are missing. Please install them first.")
    #     install_tools()
    dest = Path("./scratch")

    for port in get_connected_boards():
        log.info(f"Generating stubs for {port}")
        # check if the board is accesible and responsive
        if not run_mpremote(port, ["ls"]):
            log.error(f"Failed to connect to {port}")
            continue
        ok, my_stubs = generate_board_stubs(dest, port)
        if ok:
            log.success(f"Stubs generated for {port}")
        else:
            log.error(f"Failed to generate stubs for {port}")


if __name__ == "__main__":
    ...
    main()
