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


from typing import List, Union
from loguru import logger as log
from pathlib import Path
import subprocess
import sys
import time
import serial.tools.list_ports


def check_tools():
    """Check if all tools are available"""
    # stubber
    # pipx
    # mpremote
    return True


def install_tools():
    """Install all required tools"""
    pass


def run_mpremote(port: str, cmd: Union[str,List[str]], *, check: bool = False):  # sourcery skip: assign-if-exp
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
    mpr = subprocess.run(cmd, check=check)
    if mpr.returncode != 0:
        log.error(mpr.stderr)
        return False
    return True


def mip_install(name: str, port: str = ""):
    """Install a micropython package"""
    # install createstubs to the board
    cmd = ["mip", "install", name]
    return run_mpremote(port, cmd)


def copy_createstubs(port: str):
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
        ok = run_mpremote(port, cmd, check=False)
    return ok


def generate_board_stubs(dest: Path, port: str = ""):
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
        # ok = copy_createstubs(port)
        ok = mip_install("github:josverl/micropython-stubber/mip/full.json@board_stubber", port)
    else:
        ok = mip_install("github:josverl/micropython-stubber", port)
    if not ok:
        return False

    time.sleep(2)
    # run createstubs _mem variant

    cmd = ["mount", str(dest)] if dest else []
    cmd += ["exec", "import createstubs_mem"]

    ok = run_mpremote(port, cmd)
    if not ok:
        return False
    # post_processing(dest)

    return True


def get_connected_boards():
    """Get a list of connected boards"""
    devices = [p.device for p in serial.tools.list_ports.comports()]
    return sorted(devices)


TESTING = True


def main():
    if not check_tools():
        log.warning("Some tools are missing. Please install them first.")
        install_tools()
    dest = Path("./scratch")

    for port in get_connected_boards():
        log.info(f"Generating stubs for {port}")
        # check if the board is accesible and responsive
        if not run_mpremote(port, ["ls"], check=False):
            log.error(f"Failed to connect to {port}")
            continue
        if my_stubs := generate_board_stubs(dest, port):
            log.success(f"Stubs generated for {port}")
        else:
            log.error(f"Failed to generate stubs for {port}")


if __name__ == "__main__":
    main()
