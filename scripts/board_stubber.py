""" 
This script creates stubs for a connectes micropython MCU board.
"""
from typing import List
from loguru import logger as log
from pathlib import Path
import subprocess
import sys
import time


def check_tools():
    """Check if all tools are available"""
    # stubber
    # pipx
    # mpremote
    return True


def install_tools():
    """Install all required tools"""
    pass


def run_mpremote(port: str, cmd: List[str], *, check: bool = False):  # sourcery skip: assign-if-exp
    """Run mpremote with the given command"""
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


def mip_install(port: str, name: str = "github:josverl/micropython-stubber"):
    """Install a micropython package"""
    # install createstubs to the board
    cmd = ["mip", "install", name]
    ok = run_mpremote(port, cmd)
    return ok


def copy_createstubs(port: str):
    """Copy createstubs to theboard"""
    # copy createstubs.py to the destination folder
    do = [
        "mkdir lib",
        "cp ./src/stubber/board/createstubs_mem.py :lib/createstubs_mem.py",
        "cp ./src/stubber/board/logging.py :lib/logging.py",
        "cp ./src/stubber/board/modulelist.txt :lib/modulelist.txt",
    ]
    ok = True
    for _cmd in do:
        cmd = _cmd.split(" ")
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
    # ok = mip_install(port, "github:josverl/micropython-stubber")
    ok = copy_createstubs(port)
    if not ok:
        return False

    time.sleep(2)
    # run createstubs _mem variant
    # cmd = ["mount", str(dest), "exec", "print('wait...');import time;time.sleep(5);print('Done')"]
    cmd = ["mount", str(dest), "exec", "import createstubs_mem"]
    cmd = ["exec", "import createstubs_mem"]
    ok = run_mpremote(port, cmd)
    if not ok:
        return False
    # post_processing(dest)

    return True


#

if not check_tools():
    log.warning("Some tools are missing. Please install them first.")
    install_tools()


dest = Path("./scratch")

my_stubs = generate_board_stubs(dest)
