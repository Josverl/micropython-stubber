""" 
This script creates stubs for a connectes micropython MCU board.
"""
from loguru import logger as log
from pathlib import Path
import subprocess
import sys


def check_tools():
    """Check if all tools are available"""
    # stubber
    # pipx
    # mpremote
    return True


def install_tools():
    """Install all required tools"""
    pass


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

    # install createstubs to the board
    cmd = ["mip", "install", "github:josverl/micropython-stubber"]
    ok = run_mpremote(port, cmd)
    if not ok:
        return False

    # run createstubs _mem variant
    cmd = ["mount", str(dest), "exec", '"import createstubs"']
    ok = run_mpremote(port, cmd)
    if not ok:
        return False
    # post_processing(dest)

    return True


def run_mpremote(port, cmd):
    """Run mpremote with the given command"""
    cmd = ["mpremote", "connect", port] + cmd if port else ["mpremote"] + cmd
    log.info(" ".join(cmd))
    mpr = subprocess.run(cmd, check=True)
    if mpr.returncode != 0:
        log.error(mpr.stderr)
        return False
    return True


#

if not check_tools():
    log.warning("Some tools are missing. Please install them first.")
    install_tools()


dest = Path("./scratch/stubs")

my_stubs = generate_board_stubs(dest)
