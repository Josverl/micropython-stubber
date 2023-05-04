""" 
This script creates stubs for a connected micropython MCU board.

# MPRemote is not working properly with ESP32 boards :-( at least on Windows)
# this was fixed in the latest version of mpremote, not published yet on pypi

Workaround
pip install git+https://github.com/josverl/mpremote.git#subdirectory=tools/mpremote
"""

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tempfile import mkdtemp
from threading import Timer
from typing import List, NamedTuple, Optional, Tuple, Union

import serial.tools.list_ports
from loguru import logger as log
from tabulate import tabulate
from tenacity import retry, stop_after_attempt, wait_fixed

from stubber import utils
from stubber.publish.merge_docstubs import merge_all_docstubs
from stubber.utils.config import CONFIG

OK = 0
ERROR = -1
RETRIES = 3
TESTING = False
LOCAL_FILES = True

###############################################################################################


# @dataclass
# class LogTags:
#     reset_tags: List[str]
#     error_tags: List[str]
#     warning_tags: List[str]
#     success_tags: List[str]
#     ignore_tags: List[str]


def run(
    cmd: List[str],
    timeout: int = 60,
    log_errors: bool = True,
    no_info: bool = False,
    *,
    reset_tags: Optional[List[str]] = None,
    error_tags: Optional[List[str]] = None,
    warning_tags: Optional[List[str]] = None,
    success_tags: Optional[List[str]] = None,
    ignore_tags: Optional[List[str]] = None,
) -> Tuple[int, List[str]]:
    # sourcery skip: no-long-functions
    """
    Run a command and return the output and return code as a tuple
    Parameters
    ----------
    cmd : List[str]
        The command to run
    timeout : int, optional
        The timeout in seconds, by default 60
    log_errors : bool, optional
        If False, don't log errors, Default: true
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
    if not reset_tags:
        reset_tags = ["rst cause:1, boot mode:"]
    if not error_tags:
        error_tags = ["Traceback ", "Error: ", "Exception: ", "ERROR :", "CRIT  :"]
    if not warning_tags:
        warning_tags = ["WARN  :"]  # , "Module not found."
    if not success_tags:
        success_tags = ["Created stubs for", "Path: /remote"]
    if not ignore_tags:
        ignore_tags = ['  File "<stdin>",']

    replace_tags = ["\x1b[1A"]

    output = []
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Failed to start {cmd[0]}") from e

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
                if any(tag in line for tag in reset_tags):
                    raise Exception("Board reset detected")

                line = line.rstrip("\n")
                # if any of the error tags in the line
                if any(tag in line for tag in error_tags):
                    if not log_errors:
                        continue
                    log.error(line)
                elif any(tag in line for tag in warning_tags):
                    log.warning(line)
                elif any(tag in line for tag in success_tags):
                    log.success(line)
                elif any(tag in line for tag in ignore_tags):
                    continue
                else:
                    if not no_info:
                        log.info(line)
        if proc.stderr and log_errors:
            for line in proc.stderr:
                log.warning(line)
    finally:
        timer.cancel()

    proc.wait(timeout=1)
    return proc.returncode, output


###############################################################################################

UName = NamedTuple("UName", sysname=str, nodename=str, release=str, version=str, machine=str)


class Variant(str, Enum):
    """Variants of generatings stubs on a MCU"""

    full = "full"
    mem = "mem"
    db = "db"


class Form(str, Enum):
    """Optimisation forms of scripts"""

    py = "py"
    min = "min"
    mpy = "mpy"


class MPRemoteBoard:
    """Class to run mpremote commands"""

    def __init__(self, port: str = ""):
        self.port = port
        # self.board = ""
        self.firmware = {}
        self.uname: Optional[UName] = None
        self.connected = False
        self.path: Optional[Path] = None

    @staticmethod
    def connected_boards():
        """Get a list of connected boards"""
        devices = [p.device for p in serial.tools.list_ports.comports()]
        return sorted(devices)

    @retry(stop=stop_after_attempt(RETRIES), wait=wait_fixed(1))
    def get_uname(self):
        rc, result = self.run_command(
            ["exec", "import os;print(os.uname() if 'uname' in dir(os) else 'no.uname')"], no_info=True
        )
        s = result[0]
        if "sysname=" in s:
            self.uname = eval(f"UName{s}")
        elif s.strip() == "no.uname":
            self.uname = UName("no.uname", "?", "?", "?", "?")
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
        log_errors: bool = True,
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
        result = run(cmd, timeout, log_errors, no_info, **kwargs)
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


def copy_createstubs(board: MPRemoteBoard, variant: Variant, form: Form) -> bool:
    # sourcery skip: assign-if-exp, boolean-if-exp-identity, remove-unnecessary-cast
    """Copy createstubs to the board"""
    # copy createstubs.py to the destination folder
    _py = [
        "rm :lib/createstubs.mpy",
        "rm :lib/createstubs_mem.mpy",
        "rm :lib/createstubs_db.mpy",
        "rm :lib/createstubs.py",
        "rm :lib/createstubs_mem.py",
        "rm :lib/createstubs_db.py",
        "cp ./src/stubber/board/createstubs.py :lib/createstubs.py",
        "cp ./src/stubber/board/createstubs_mem.py :lib/createstubs_mem.py",
        "cp ./src/stubber/board/createstubs_db.py :lib/createstubs_db.py",
        "cp ./src/stubber/board/logging.py :lib/logging.py",
    ]
    # copy createstubs*_min.py to the destination folder
    _min = [
        "cp ./src/stubber/board/createstubs_min.py :lib/createstubs.py",
        "cp ./src/stubber/board/createstubs_mem_min.py :lib/createstubs_mem.py",
        "cp ./src/stubber/board/createstubs_db_min.py :lib/createstubs_db.py",
    ]
    # copy createstubs*_mpy.mpy to the destination folder
    _mpy = [
        "rm :lib/createstubs.py",
        "rm :lib/createstubs_mem.py",
        "rm :lib/createstubs_db.py",
        "cp ./src/stubber/board/createstubs_mpy.mpy :lib/createstubs.mpy",
        "cp ./src/stubber/board/createstubs_mem_mpy.mpy :lib/createstubs_mem.mpy",
        "cp ./src/stubber/board/createstubs_db_mpy.mpy :lib/createstubs_db.mpy",
    ]

    _lib = [["exec", "import os;os.mkdir('lib') if not ('lib' in os.listdir()) else print('folder lib already exists')"]]

    _get_ready = [
        "rm :modulelist.done",
        "cp ./src/stubber/board/modulelist.txt :lib/modulelist.txt",
        # "cp ./board_info.csv :lib/board_info.csv",
    ]
    if form == Form.py:
        do = _lib + _py + _get_ready
    elif form == Form.min:
        do = _lib + _min + _get_ready
    else:
        do = _lib + _mpy + _get_ready

    # assume all ok, unless one is not ok
    for cmd in do:
        if isinstance(cmd, str) and cmd.startswith("rm "):
            log_errors = False
        else:
            log_errors = True
        rc, _ = board.run_command(cmd, log_errors=log_errors)
        if rc != OK and "rm" not in cmd:
            log.error(f"Error during copy createstubs running command: {cmd}")
            return False
    return True


@retry(stop=stop_after_attempt(4), wait=wait_fixed(2))
def hard_reset(board: MPRemoteBoard) -> bool:
    """Reset the board"""
    rc, _ = board.run_command(["soft-reset", "exec", "import machine;machine.reset()"], timeout=5)
    board.connected = False
    return rc == OK


@retry(stop=stop_after_attempt(10), wait=wait_fixed(15))
def run_createstubs(dest: Path, board: MPRemoteBoard, variant: Variant = Variant.db):
    """Run createstubs on the board"""
    # hard_reset(board)

    # add the lib folder to the path
    cmd_path = ["exec", 'import sys;sys.path.append("/lib") if "/lib" not in sys.path else "/lib already in path"']
    board.run_command(cmd_path, timeout=5)

    cmd = build_cmd(dest, variant)
    board.run_command.retry.wait = wait_fixed(15)
    # some boards need 2-3 minutes so increase timeout
    #  but slows down esp8266 restarts so keep that to 60 seconds
    timeout = 60 if board.uname.nodename == "esp8266" else 4 * 60
    rc, out = board.run_command(cmd, timeout=timeout)
    # check last line for exception or error and raise that if found
    if rc != OK and ":" in out[-1] and not out[-1].startswith("INFO") and not out[-1].startswith("WARN"):
        log.warning(f"createstubs: {out[-1]}")
        raise RuntimeError(out[-1]) from eval(out[-1].split(":")[0])

    if rc != OK and variant == Variant.db:
        # assume createstubs ran out of memory and try again
        raise MemoryError("Memory error, try again")
    return rc, out


def build_cmd(dest: Path, variant: Variant = Variant.db):
    """Build the import createstubs[_??] command to run on the board"""
    cmd = ["mount", str(dest)] if dest else []
    if variant == Variant.db:
        cmd += ["exec", "import createstubs_db"]
    elif variant == Variant.mem:
        cmd += ["exec", "import createstubs_mem"]
    else:
        cmd += ["exec", "import createstubs"]
    return cmd


def generate_board_stubs(
    dest: Path, mcu: MPRemoteBoard, variant: Variant = Variant.db, form: Form = Form.mpy
) -> Tuple[int, Optional[Path]]:
    """
    Generate the board stubs.
    Parameters
    ----------
    dest : Path
        The destination folder for the stubs
    port : str
        The port the board is connected to
    """

    board_info_path = Path(__file__).parent.parent / "board_info.csv"
    # HOST -> MCU : copy createstubs to board
    if LOCAL_FILES:
        ok = copy_createstubs(mcu, variant, form)
    else:
        # TODO: Add Branch to install from
        ok = mcu.mip_install("github:josverl/micropython-stubber")
    if not ok and not TESTING:
        log.warning("Error copying createstubs to board")
        return ERROR, None
    # HOST: remove .done file
    (dest / "modulelist.done").unlink(missing_ok=True)
    # HOST: copy board_info.csv to destination
    shutil.copyfile(board_info_path, dest / "board_info.csv")

    # MCU: add lib to path
    rc, out = run_createstubs(dest, mcu, variant)

    if rc != OK:
        log.warning("Error running createstubs: %s", out)
        return ERROR, None

    # Find the output starting with 'Path: '
    folder = get_stubfolder(out)
    if not folder:
        return ERROR, None

    stubs_path = dest / folder
    mcu.path = stubs_path
    # read the modles.json file into a dict
    try:
        with open(stubs_path / "modules.json") as fp:
            modules_json = json.load(fp)
            mcu.firmware = modules_json["firmware"]
    except FileNotFoundError:
        log.warning("Error generating stubs, modules.json not found")
        return ERROR, None

    # check the number of stubs generated
    if len(list(stubs_path.glob("*.p*"))) < 10:
        log.warning("Error generating stubs, too few (<10)stubs were generated")
        return ERROR, None

    utils.do_post_processing([stubs_path], pyi=True, black=True)

    return OK, stubs_path


def get_stubfolder(out: List[str]):
    return lines[-1].split("/remote/")[-1].strip() if (lines := [l for l in out if l.startswith("Path: ")]) else ""


# def get_port_board(out: List[str]):
#     return (
#         lines[-1].split("Port:")[-1].strip() if (lines := [l for l in out if l.startswith("Port: ")]) else "",
#         lines[-1].split("Board:")[-1].strip() if (lines := [l for l in out if l.startswith("Board: ")]) else "",
#     )


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
            _, uname = board.get_uname()
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
        format_str = (
            "<green>{time:HH:mm:ss}</green>|<level>{level: <8}</level>|<cyan>{module: <20}</cyan> - <level>{message}</level>"
        )
    else:
        format_str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>|<level>{level: <8}</level>|<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    log.add(sys.stderr, level=level, backtrace=True, diagnose=True, colorize=True, format=format_str)
    # log.info(f"micropython-stubber {__version__}")
    return level


def copy_to_repo(source: Path) -> Optional[Path]:
    """Copy the generated stubs to the stubs repo.
    If the destination folder exists, it is first emptied
    when succesfull: returns the destination path - None otherwise
    """
    destination = CONFIG.stub_path / source.name
    try:
        if destination.exists() and destination.is_dir():
            # first clean the destination folder
            shutil.rmtree(destination)
        # copy all files and folder from the source to the destination
        shutil.copytree(source, destination, dirs_exist_ok=True)
        return destination
    except OSError as e:
        log.error(f"Error: {source} : {e.strerror}")
        return None


if __name__ == "__main__":
    set_loglevel(2)

    variant = Variant.db
    form = Form.py
    tempdir = mkdtemp(prefix="board_stubber")

    dest = Path(tempdir)
    # copy board_info.csv to the folder
    # shutil.copyfile(Path("board_info.csv"), dest / "board_info.csv")

    # scan boards and just work with the ones that reponded with understandable data
    connected_boards = scan_boards(True)
    if not connected_boards:
        log.error("No micropython boards were found")
        sys.exit(1)

    print(tabulate([[b.port] + (list(b.uname) if b.uname else ["unable to connect"]) for b in connected_boards]))  # type: ignore
    # scan boards and generate stubs

    for board in connected_boards:
        log.info(f"Connecting to {board.port} {board.uname[4] if board.uname else ''}")
        rc, my_stubs = generate_board_stubs(dest, board, variant, form)
        if rc == OK:
            log.success(f'Stubs generated for {board.firmware["port"]}-{board.firmware["board"]}')
            if destination := copy_to_repo(my_stubs):
                log.success(f"Stubs copied to {destination}")
                # Also merge the stubs with the docstubs
                log.info(f"Merging stubs with docstubs : {board.firmware}")

                _ = merge_all_docstubs(
                    versions=board.firmware["version"],
                    family=board.firmware["family"],
                    boards=board.firmware["board"],
                    ports=board.firmware["port"],
                    mpy_path=CONFIG.mpy_path,
                )
                log.success("Done")

                # Then Build the package

        else:
            log.error(f"Failed to generate stubs for {board.port}")
