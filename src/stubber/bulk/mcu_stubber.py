""" 
This script creates stubs on and for a connected micropython MCU board.
"""

import json
import shutil
import sys
import time
from enum import Enum
from pathlib import Path
from tempfile import mkdtemp
from typing import List, Optional, Tuple

from rich.console import Console
from rich.table import Table
from tenacity import retry, stop_after_attempt, wait_fixed

from mpflash.connected import list_mcus
from mpflash.list import show_mcus
from mpflash.logger import log
from mpflash.mpremoteboard import ERROR, OK, MPRemoteBoard
from stubber import utils
from stubber.publish.merge_docstubs import merge_all_docstubs
from stubber.publish.pathnames import board_folder_name
from stubber.publish.publish import build_multiple
from stubber.utils.config import CONFIG

HERE = Path(__file__).parent
###############################################################################################
# TODO: promote to cmdline params
LOCAL_FILES = False
reset_before = True
TESTING = False
###############################################################################################


###############################################################################################


class Variant(str, Enum):
    """Variants to generate stubs on a MCU"""

    full = "full"
    mem = "mem"
    db = "db"


class Form(str, Enum):
    """Optimization forms of scripts"""

    py = "py"
    min = "min"
    mpy = "mpy"


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
    if rc != OK and out and ":" in out[-1] and not out[-1].startswith("INFO") and not out[-1].startswith("WARN"):
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
    host_mounted: bool = True,
) -> Tuple[int, Optional[Path]]:
    """
    Generate the MCU stubs for this MCU board.
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
        log.warning("Could not load modules.json, Assuming error in createstubs")
        return ERROR, None

    # check the number of stubs generated
    if len(list(stubs_path.glob("*.p*"))) < 10:
        log.warning("Error generating stubs, too few (<10)stubs were generated")
        return ERROR, None

    stubgen_needed = any(stubs_path.glob("*.py"))
    utils.do_post_processing([stubs_path], stubgen=stubgen_needed, black=True, autoflake=True)

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
        cmd = [
            "exec",
            f"with open('lib/boardname.py', 'w') as f: f.write('BOARDNAME=\"{mcu.board}\"')",
        ]
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
    return lines[-1].split("/remote/")[-1].strip() if (lines := [l for l in out if l.startswith("INFO  : Path: ")]) else ""


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
    when successful: returns the destination path - None otherwise
    """
    destination = CONFIG.stub_path / board_folder_name(fw)
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


def stub_connected_mcus(
    variant: str,
    format: str,
    debug: bool,
    serial: List[str],
    ignore: List[str],
    bluetooth: bool,
) -> int:
    """
    Runs the stubber to generate stubs for connected MicroPython boards.

    Args:
        variant (str): The variant of the createstubs script.
        format (str): The format of the createstubs script.
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
    temp_path = Path(tempdir)

    all_built = []

    # scan boards and just work with the ones that respond with understandable data
    connected_mcus = list_mcus(ignore=ignore, include=serial, bluetooth=bluetooth)
    # ignore boards that have the [micropython-stubber] ignore flag set
    connected_mcus = [item for item in connected_mcus if not (item.toml.get("micropython-stubber", {}).get("ignore", False))]

    if not connected_mcus:
        log.error("No micropython boards were found")
        return ERROR

    show_mcus(connected_mcus, refresh=False)

    # scan boards and generate stubs
    for board in connected_mcus:
        log.info(f"Connecting using {board.serialport} to {board.port} {board.board} {board.version}: {board.description}")
        # remove the modulelist.done file before starting createstubs on each board
        (temp_path / "modulelist.done").unlink(missing_ok=True)

        rc, my_stubs = generate_board_stubs(temp_path, board, variant, form)
        if rc != OK:
            log.error(f"Failed to generate stubs for {board.serialport}")
            continue
        if my_stubs:
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
                all_built.extend(built)

    if all_built:
        print_result_table(all_built)
        log.success("Done")
        return OK
    log.error(f"Failed to generate stubs for {board.serialport}")
    return ERROR


def print_result_table(all_built: List, console: Optional[Console] = None):
    if not console:
        console = Console()
    # create a rich table of the results and print it'
    table = Table(title="Results")

    table.add_column("Result", style="cyan")
    table.add_column("Name/Path", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Error", style="red")

    for result in all_built:
        table.add_row(
            result["result"],
            (result["name"] + "\n" + result["path"]).strip(),
            result["version"],
            result["error"],
        )
    console.print(table)
