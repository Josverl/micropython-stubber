""" 
This script creates stubs on and for a connected micropython MCU board.
"""

import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tempfile import mkdtemp
from threading import Timer
from typing import List, NamedTuple, Optional, Tuple, Union

import rich_click as click
import serial.tools.list_ports
from loguru import logger as log
from rich.console import Console
from rich.table import Table
from tenacity import retry, stop_after_attempt, wait_fixed

from stubber import utils
from stubber.publish.merge_docstubs import get_board_path, merge_all_docstubs
from stubber.publish.publish import build_multiple
from stubber.utils.config import CONFIG

OK = 0
ERROR = -1
RETRIES = 3
TESTING = False
LOCAL_FILES = True

###############################################################################################
reset_before = True
###############################################################################################


@dataclass
class LogTags:
    reset_tags: List[str]
    error_tags: List[str]
    warning_tags: List[str]
    success_tags: List[str]
    ignore_tags: List[str]


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
        warning_tags = ["WARN  :", "TRACE :"]  # , "Module not found."
    if not success_tags:
        success_tags = ["Created stubs for", "Path: /remote"]
    if not ignore_tags:
        ignore_tags = ['  File "<stdin>",']

    replace_tags = ["\x1b[1A"]

    output = []
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding="utf-8",
        )
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
                    raise RuntimeError("Board reset detected")

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
    return proc.returncode or 0, output


###############################################################################################


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

    def __init__(self, serialport: str = ""):
        self.serialport = serialport
        # self.board = ""
        self.firmware = {}

        self.connected = False
        self.path: Optional[Path] = None
        self.description = ""
        self.version = ""
        self.port = ""
        self.board = ""

    @staticmethod
    def connected_boards():
        """Get a list of connected boards"""
        devices = [p.device for p in serial.tools.list_ports.comports()]
        return sorted(devices)

    @retry(stop=stop_after_attempt(RETRIES), wait=wait_fixed(1))
    def get_mcu_info(self):
        rc, result = self.run_command(
            ["run", "src/stubber/board/fw_info.py"],
            no_info=True,
        )
        if rc != OK:
            raise RuntimeError(f"Failed to get mcu_info for {self.serialport}")
        # Ok we have the info, now parse it
        s = result[0].strip()
        if s.startswith("{") and s.endswith("}"):
            info = eval(s)
            self.version = info["version"]
            self.port = info["port"]
            self.description = descr = info["board"]
            pos = descr.rfind(" with")
            if pos != -1:
                short_descr = descr[:pos].strip()
            else:
                short_descr = ""
            if board_name := find_board(
                descr, short_descr, Path(__file__).parent.parent / "src/stubber/data/board_info.csv"
            ):
                self.board = board_name
            else:
                self.board = "UNKNOWN"

    def disconnect(self) -> bool:
        """Disconnect from a board"""
        if not self.connected:
            return True
        if not self.serialport:
            log.error("No port connected")
            self.connected = False
            return False
        log.info(f"Disconnecting from {self.serialport}")
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
        prefix = [sys.executable, "-m", "mpremote", "connect", self.serialport] if self.serialport else ["mpremote"]
        # if connected add resume to keep state between commands
        if self.connected:
            prefix += ["resume"]
        cmd = prefix + cmd
        log.debug(" ".join(cmd))
        result = run(cmd, timeout, log_errors, no_info, **kwargs)
        self.connected = result[0] == OK
        return result

    @retry(stop=stop_after_attempt(RETRIES), wait=wait_fixed(1))
    def mip_install(self, name: str) -> bool:
        """Install a micropython package"""
        # install createstubs to the board
        cmd = ["mip", "install", name]
        result = self.run_command(cmd)[0] == OK
        self.connected = True
        return result


def copy_createstubs_to_board(board: MPRemoteBoard, variant: Variant, form: Form) -> bool:
    # sourcery skip: assign-if-exp, boolean-if-exp-identity, remove-unnecessary-cast
    """Copy createstubs to the board"""
    # copy createstubs.py to the destination folder
    origin = "./src/stubber/board"

    _py = [
        "rm :lib/createstubs.mpy",
        "rm :lib/createstubs_mem.mpy",
        "rm :lib/createstubs_db.mpy",
        "rm :lib/createstubs.py",
        "rm :lib/createstubs_mem.py",
        "rm :lib/createstubs_db.py",
        f"cp {origin}/createstubs.py :lib/createstubs.py",
        f"cp {origin}/createstubs_mem.py :lib/createstubs_mem.py",
        f"cp {origin}/createstubs_db.py :lib/createstubs_db.py",
        f"cp {origin}/logging.py :lib/logging.py",
    ]
    # copy createstubs*_min.py to the destination folder
    _min = [
        f"cp {origin}/createstubs_min.py :lib/createstubs.py",
        f"cp {origin}/createstubs_mem_min.py :lib/createstubs_mem.py",
        f"cp {origin}/createstubs_db_min.py :lib/createstubs_db.py",
    ]
    # copy createstubs*_mpy.mpy to the destination folder
    _mpy = [
        "rm :lib/createstubs.py",
        "rm :lib/createstubs_mem.py",
        "rm :lib/createstubs_db.py",
        f"cp {origin}/createstubs_mpy.mpy :lib/createstubs.mpy",
        f"cp {origin}/createstubs_mem_mpy.mpy :lib/createstubs_mem.mpy",
        f"cp {origin}/createstubs_db_mpy.mpy :lib/createstubs_db.mpy",
    ]

    _lib = [
        [
            "exec",
            "import os;os.mkdir('lib') if not ('lib' in os.listdir()) else print('folder lib already exists')",
        ]
    ]

    _get_ready = [
        "rm :modulelist.done",
        "rm :no_auto_stubber.txt",
        f"cp {origin}/modulelist.txt :lib/modulelist.txt",
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
    # do not run  "exec", "import machine;machine.reset()" as it will hang an esp32
    rc, _ = board.run_command(["reset"], timeout=5)
    board.connected = False
    return rc == OK


@retry(stop=stop_after_attempt(10), wait=wait_fixed(15))
def run_createstubs(dest: Path, mcu: MPRemoteBoard, variant: Variant = Variant.db):
    """
    Run a createstubs[variant]  on the provided board.
    Retry running the command up to 10 times, with a 15 second timeout between retries.
    this should allow for the boards with little memory to complete even if they run out of memory.
    """
    # add the lib folder to the path
    cmd_path = [
        "exec",
        'import sys;sys.path.append("/lib") if "/lib" not in sys.path else "/lib already in path"',
    ]
    mcu.run_command(cmd_path, timeout=5)

    if reset_before:
        log.info(f"Resetting {mcu.serialport} {mcu.description}")
        mcu.run_command("reset", timeout=5)
        time.sleep(2)

    log.info(f"Running createstubs {variant.value} on {mcu.serialport} {mcu.description} using temp path: {dest}")
    cmd = build_cmd(dest, variant)
    log.info(f"Running : mpremote {' '.join(cmd)}")
    mcu.run_command.retry.wait = wait_fixed(15)
    # some boards need 2-3 minutes to run createstubs - so increase the default timeout
    # esp32s3 > 240 seconds with mounted fs
    #  but slows down esp8266 restarts so keep that to 90 seconds
    timeout = 90 if mcu.port == "esp8266" else 6 * 60  # type: ignore
    rc, out = mcu.run_command(cmd, timeout=timeout)
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
    dest: Path,
    mcu: MPRemoteBoard,
    variant: Variant = Variant.db,
    form: Form = Form.mpy,
    host_mounted=True,
) -> Tuple[int, Optional[Path]]:
    """
    Generate the board stubs for this MCU board.
    Parameters
    ----------
    dest : Path
        The destination folder for the stubs
    port : str
        The port the board is connected to
    """

    # HOST -> MCU : copy createstubs to board
    ok = copy_scripts_to_board(mcu, variant, form)
    if not ok and not TESTING:
        log.warning("Error copying createstubs to board")
        return ERROR, None

    copy_boardname_to_board(mcu)

    rc, out = run_createstubs(dest, mcu, variant)  # , host_mounted=host_mounted)

    if rc != OK:
        log.warning("Error running createstubs: %s", out)
        return ERROR, None

    if not host_mounted:
        # Waiting for MPRemote to support copying folder from board to host
        raise NotImplementedError("TODO: Copy stubs from board to host")

    # Find the output starting with 'Path: '
    folder = get_stubfolder(out)
    if not folder:
        return ERROR, None

    stubs_path = dest / folder
    mcu.path = stubs_path
    # read the modules.json file into a dict
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

    utils.do_post_processing([stubs_path], stubgen=True, black=True, autoflake=True)

    return OK, stubs_path


def copy_boardname_to_board(mcu: MPRemoteBoard):
    """
    Copies the board name to the board by writing it to the 'boardname.py' file.

    Args:
        mcu: The MCU object representing the microcontroller.

    Returns:
        None
    """
    if mcu.board:
        cmd = ["exec", f"with open('lib/boardname.py', 'w') as f: f.write('BOARDNAME=\"{mcu.board}\"')"]
        log.info(f"Writing BOARDNAME='{mcu.board}' to boardname.py")
    else:
        cmd = ["rm", "boardname.py"]
    rc, _ = mcu.run_command(cmd)
    if rc != OK and "rm" not in cmd:
        log.error(f"Error during copy createstubs running command: {cmd}")


def copy_scripts_to_board(mcu: MPRemoteBoard, variant: Variant, form: Form):
    """
    Copy scripts to the board.

    Args:
        mcu (str): The microcontroller unit.
        variant (str): The variant of the board.
        form (Form): The form of the scripts to be copied.

    Returns:
        bool: True if the scripts are successfully copied, False otherwise.
    """
    if LOCAL_FILES:
        return copy_createstubs_to_board(mcu, variant, form)
    if form == Form.min:
        location = "github:josverl/micropython-stubber/mip/minified.json"
    elif form == Form.mpy:
        location = "github:josverl/micropython-stubber/mip/mpy_v6.json"
    else:
        location = "github:josverl/micropython-stubber/mip/full.json"

    return mcu.mip_install(location)


def get_stubfolder(out: List[str]):
    return lines[-1].split("/remote/")[-1].strip() if (lines := [l for l in out if l.startswith("Path: ")]) else ""


def scan_boards(optimistic: bool = False) -> List[MPRemoteBoard]:
    """
    This function scans for boards and returns a list of MPRemoteBoard objects.
    :return: list of MPRemoteBoard objects
    """
    boards = []
    for mpr_port in MPRemoteBoard.connected_boards():
        board = MPRemoteBoard(mpr_port)
        log.info(f"Attempt to connect to: {board.serialport}")
        try:
            board.get_mcu_info()
            log.success(f"Detected board {board.description} {board.version}")
            boards.append(board)
        except Exception:
            log.error(f"Failed to get mcu_info for {board.serialport}")
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


def copy_to_repo(source: Path, fw: dict) -> Optional[Path]:
    """Copy the generated stubs to the stubs repo.
    If the destination folder exists, it is first emptied
    when succesfull: returns the destination path - None otherwise
    """
    # destination = CONFIG.stub_path / source.name
    destination = get_board_path(fw)
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


def find_board(descr: str, short_descr: str, filename: Path) -> Optional[str]:
    "Find the board in the provided board_info.csv file"
    short_hit = ""
    with open(filename, "r") as file:
        # ugly code to make testable in python and micropython
        # TODO: This is VERY slow on micropython whith MPREMOTE mount on esp32 (2-3 minutes to read file)
        while 1:
            line = file.readline()
            if not line:
                break
            descr_, board_ = line.split(",")[0].strip(), line.split(",")[1].strip()
            if descr_ == descr:
                return board_
            elif short_descr and descr_ == short_descr:
                if "with" in short_descr:
                    # Good enough - no need to trawl the entire file
                    # info["board"] = board_
                    return board_
                # good enough if not found in the rest of the file (but slow)
                short_hit = board_
    if short_hit:
        return short_hit
    return None


@click.command()
@click.option(
    "--variant",
    "-v",
    type=click.Choice(["Full", "Mem", "DB"], case_sensitive=False),
    default="Full",
    show_default=True,
    help="Variant of createstubs to run",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["py", "mpy"], case_sensitive=False),
    default="py",
    show_default=True,
    help="Python source or pre-compiled.",
)
@click.option("--debug/--no-debug", default=False, show_default=True, help="Debug mode.")
def run_stubber_connected_boards(variant: str, format: str, debug: bool):
    """
    Runs the stubber to generate stubs for connected MicroPython boards.

    Args:
        variant (str): The variant of the MicroPython board.
        format (str): The format of the generated stubs.
        debug (bool): Flag indicating whether to enable debug mode.

    Returns:
        None
    """

    if debug:
        set_loglevel(1)
    else:
        set_loglevel(0)
    variant = Variant(variant.lower())
    form = Form(format.lower())

    tempdir = mkdtemp(prefix="board_stubber")

    dest = Path(tempdir)

    # scan boards and just work with the ones that reponded with understandable data
    connected_boards = scan_boards(True)
    if not connected_boards:
        log.error("No micropython boards were found")
        sys.exit(1)

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Serial Port")
    table.add_column("Port")
    table.add_column("Description")
    table.add_column("Version")

    for b in connected_boards:
        table.add_row(b.serialport, b.port, b.description, b.version)
    console = Console()
    console.print(table)

    # scan boards and generate stubs
    for board in connected_boards:
        log.info(
            f"Connecting using {board.serialport} to {board.port} {board.board} {board.version}: {board.description}"
        )

        rc, my_stubs = generate_board_stubs(dest, board, variant, form)
        if rc == OK and my_stubs:
            log.success(f'Stubs generated for {board.firmware["port"]}-{board.firmware["board"]}')
            if destination := copy_to_repo(my_stubs, board.firmware):
                log.success(f"Stubs copied to {destination}")
                # Also merge the stubs with the docstubs
                log.info(f"Merging stubs with docstubs : {board.firmware}")

                merged = merge_all_docstubs(
                    versions=board.firmware["version"],
                    family=board.firmware["family"],
                    boards=board.firmware["board"],
                    ports=board.firmware["port"],
                    mpy_path=CONFIG.mpy_path,
                )
                if not merged:
                    log.error(f"Failed to merge stubs for {board.serialport}")
                    continue
                # Then Build the package
                log.info(f"Building package for {board.firmware}")
                built = build_multiple(
                    versions=board.firmware["version"],
                    family=board.firmware["family"],
                    boards=board.firmware["board"],
                    ports=board.firmware["port"],
                )
                # create a rich table of the results and print it'
                console.print(table)
                log.success("Done")
        else:
            log.error(f"Failed to generate stubs for {board.serialport}")


if __name__ == "__main__":
    run_stubber_connected_boards()
