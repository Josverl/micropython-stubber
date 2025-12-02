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
from typing import List, Optional, Tuple, Union

from mpflash.connected import list_mcus
from mpflash.list import show_mcus
from mpflash.logger import log
from mpflash.mpremoteboard import ERROR, OK, MPRemoteBoard
from rich.console import Console
from rich.table import Table
from tenacity import retry, stop_after_attempt, wait_fixed

from stubber import utils
from stubber.publish.merge_docstubs import merge_all_docstubs
from stubber.publish.pathnames import board_folder_name
from stubber.publish.publish import build_multiple
from stubber.utils.config import CONFIG

HERE = Path(__file__).parent
###############################################################################################
# TODO: promote to cmdline params
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


@retry(stop=stop_after_attempt(4), wait=wait_fixed(2))
def hard_reset(board: MPRemoteBoard) -> bool:
    """Reset the board"""
    # do not run  "exec", "import machine;machine.reset()" as it will hang an esp32
    rc, _ = board.run_command(["reset"], timeout=5)
    board.connected = False
    return rc == OK


@retry(stop=stop_after_attempt(10), wait=wait_fixed(15))
def run_createstubs(
    dest: Path,
    mcu: MPRemoteBoard,
    variant: Variant = Variant.db,
    mount_vfs: bool = True,
):
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
    if mount_vfs:
        cmd = build_cmd(dest, variant)
    else:
        mcu.run_command(["rm", ":modulelist.done"], log_errors=False)
        cmd = build_cmd(None, variant)
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


def build_cmd(dest: Union[Path, None], variant: Variant = Variant.db) -> List[str]:
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
    mount_vfs: bool = True,
    exclude: Union[List[str], None] = None,
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
    exclude = exclude or []
    # TODO: use remaining free memory to determine if we can afford to mount the vfs
    if mcu.cpu.lower() == "esp8266":
        # insuficcient memory on the board also mount a remote fs
        mount_vfs = False
    if not mount_vfs:
        # remove prio stubs folder to avoid running out of flash space
        mcu.run_command(["rm", "-rv", ":stubs"], log_errors=False)
    # HOST -> MCU : mip install createstubs to board
    ok = install_scripts_to_board(mcu, form)
    if not ok and not TESTING:
        log.warning("Error copying createstubs to board")
        return ERROR, None
    # the MCU board may not have a board id,so lets just provide it so
    # createstubs can use it if needed.
    copy_boardname_to_board(mcu)

    # Copy exclude list to board if provided
    if exclude:
        exclude_file = dest / "modulelist_exclude.txt"
        exclude_file.write_text("\n".join(exclude) + "\n")
        log.info(f"Uploading exclude list with {len(exclude)} module(s): {', '.join(exclude)}")
        mcu.run_command(["cp", str(exclude_file), ":modulelist_exclude.txt"])

    rc, out = run_createstubs(dest, mcu, variant, mount_vfs=mount_vfs)

    if rc != OK:
        log.warning("Error running createstubs: %s", out)
        return ERROR, None

    if mount_vfs:
        folder = get_stubfolder(out)
    else:
        # Waiting for MPRemote to support copying folder from board to host
        cmd = f"cp -r :stubs {dest.as_posix()}"
        log.info(f"Copy stubs from board to host: {cmd}")
        mcu.run_command(cmd, timeout=60)
        # drop the first `/` from the pathto avoid absolute path
        folder = get_stubfolder(out).lstrip("/")

    # Find the output starting with 'Path: '
    if not folder:
        return ERROR, None

    stubs_path = dest / folder
    mcu.path = stubs_path
    # read the modules.json file into a dict
    try:
        with open(stubs_path / "modules.json", encoding="utf-8") as fp:
            modules_json = json.load(fp)
            mcu.firmware = modules_json["firmware"]
        log.debug(f"Found modules.json: {modules_json}")
    except FileNotFoundError:
        log.warning("Could not load modules.json, Assuming error in createstubs")
        return ERROR, None

    # check the number of stubs generated
    if len(list(stubs_path.glob("*.p*"))) < 10:
        log.warning("Error generating stubs, too few (<10)stubs were generated")
        return ERROR, None
    log.debug(f"Found {len(list(stubs_path.glob('*.p*')))} stubs")

    stubgen_needed = any(stubs_path.glob("*.py"))
    utils.do_post_processing([stubs_path], stubgen=stubgen_needed, format=True, autoflake=True)

    return OK, stubs_path


def copy_boardname_to_board(mcu: MPRemoteBoard):
    """
    Copies the board name to the board by writing it to the 'boardname.py' file.

    Args:
        mcu: The MCU object representing the microcontroller.

    Returns:
        None
    """
    if mcu.board_id:
        cmd = [
            "exec",
            f"with open('lib/boardname.py', 'w') as f: f.write('BOARD_ID=\"{mcu.board_id}\"')",
        ]
        log.info(f"Writing BOARD_ID='{mcu.board_id}' to boardname.py")
    else:
        cmd = ["rm", "boardname.py"]
    rc, _ = mcu.run_command(cmd)
    if rc != OK and "rm" not in cmd:
        log.error(f"Error during copy createstubs running command: {cmd}")


def install_scripts_to_board(mcu: MPRemoteBoard, form: Form):
    """
    Copy the createstubs script(s) to the board.
    The scripts are sourced from the 'board' folder that is included
     - in the micropython-stubber package.
     - or in de repo during development

    Args:
        mcu (str): The microcontroller unit.
        variant (str): The variant of the board.
        form (Form): The form of the scripts to be copied.

    Returns:
        bool: True if the scripts are successfully copied, False otherwise.
    """
    if form == Form.mpy:
        location = "pkg_mpy.json"
    elif form == Form.min:
        location = "pkg_minified.json"
    else:
        location = "pkg_full.json"
    location = f"{HERE.parent.absolute().as_posix()}/board/{location}"
    log.info(f"Installing {location} to {mcu.serialport} {mcu.description}")
    return mcu.mip_install(location)


def get_stubfolder(out: List[str]):
    line = lines[-1] if (lines := [l for l in out if l.startswith("INFO  : Path: ")]) else ""
    if "/remote/" in line:
        # the path is on a remote vfs, so we need to split it and return the last part
        return line.split("/remote/")[-1].strip()
    else:
        # the path is on the local vfs, so just use the path
        return line.split("Path:")[-1].strip()


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

    log.add(
        sys.stderr,
        level=level,
        backtrace=True,
        diagnose=True,
        colorize=True,
        format=format_str,
    )
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
    exclude: Union[List[str], None] = None,
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
    exclude = exclude or []
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

        rc, my_stubs = generate_board_stubs(temp_path, board, variant, form, exclude=exclude)
        if rc != OK:
            log.error(f"Failed to generate stubs for {board.serialport}")
            continue
        if my_stubs:
            log.success(f"Stubs generated for {board.firmware['port']}-{board.firmware['board']}")
            if destination := copy_to_repo(my_stubs, board.firmware):
                log.success(f"Stubs copied to {destination}")
                # Also merge the stubs with the docstubs
                log.info(f"Merging stubs with docstubs : {board.firmware}")

                merged = merge_all_docstubs(
                    versions=board.firmware["version"],
                    family=board.firmware["family"],
                    boards=board.firmware["board"],
                    ports=board.firmware["port"],
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
    # log.error(f"Failed to generate stubs for {board.serialport}")
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
