import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import jsonlines
from loguru import logger as log

from mpflash.mpremoteboard import MPRemoteBoard

from .common import FWInfo, clean_version
from .config import config

# #########################################################################################################
WorkList = List[Tuple[MPRemoteBoard, FWInfo]]


# #########################################################################################################
def local_firmwares(fw_folder: Path) -> List[FWInfo]:
    """Load a list of locally available  firmwares from the jsonl file"""
    firmwares: List[FWInfo] = []
    try:
        with jsonlines.open(fw_folder / "firmware.jsonl") as reader:
            firmwares.extend(iter(reader))
    except FileNotFoundError:
        log.error(f"No firmware.jsonl found in {fw_folder}")
    # sort by filename
    firmwares.sort(key=lambda x: x["filename"])
    return firmwares


def find_firmware(
    *,
    board: str,
    version: str = "",
    port: str = "",
    variants: bool = False,
    fw_folder: Optional[Path] = None,
    trie: int = 1,
    selector: Optional[Dict[str, str]] = None,
) -> List[FWInfo]:
    if selector is None:
        selector = {}
    fw_folder = fw_folder or config.firmware_folder
    # Use the information in firmwares.jsonl to find the firmware file
    fw_list = local_firmwares(fw_folder)
    if not fw_list:
        log.error("No firmware files found. Please download the firmware first.")
        return []
    # filter by version
    version = clean_version(version, drop_v=True)
    fw_list = filter_fwlist(fw_list, board, version, port, variants, selector)

    if not fw_list and trie < 2:
        board_id = board.replace("_", "-")
        # ESP board naming conventions have changed by adding a PORT refix
        if port.startswith("esp") and not board_id.startswith(port.upper()):
            board_id = f"{port.upper()}_{board_id}"
        # RP2 board naming conventions have changed by adding a _RPIprefix
        if port == "rp2" and not board_id.startswith("RPI_"):
            board_id = f"RPI_{board_id}"

        log.info(f"Try ({trie}) to find a firmware for the board {board_id}")
        fw_list = find_firmware(
            fw_folder=fw_folder,
            board=board_id,
            version=version,
            port=port,
            trie=trie + 1,
            selector=selector,
        )
        # hope we have a match now for the board
    # sort by filename
    fw_list.sort(key=lambda x: x["filename"])
    return fw_list


def filter_fwlist(
    fw_list: List[FWInfo],
    board: str,
    version: str,
    port: str,
    # preview: bool,
    variants: bool,
    selector: dict,
) -> List[FWInfo]:
    """Filter the firmware list based on the provided parameters"""
    if "preview" in version:
        # never get a preview for an older version
        fw_list = [fw for fw in fw_list if fw["preview"]]
    else:
        fw_list = [fw for fw in fw_list if fw["version"] == version]

    # filter by port
    if port:
        fw_list = [fw for fw in fw_list if fw["port"] == port]

    if board:
        if variants:
            fw_list = [fw for fw in fw_list if fw["board"] == board]
        else:
            # the variant should match exactly the board name
            fw_list = [fw for fw in fw_list if fw["variant"] == board]
    if selector and port in selector:
        fw_list = [fw for fw in fw_list if fw["filename"].endswith(selector[port])]
    return fw_list


# #########################################################################################################
#


def auto_update(
    conn_boards: List[MPRemoteBoard],
    target_version: str,
    fw_folder: Path,
    *,
    selector: Optional[Dict[str, str]] = None,
) -> WorkList:
    """Builds a list of boards to update based on the connected boards and the firmware available"""
    if selector is None:
        selector = {}
    wl: WorkList = []
    for mcu in conn_boards:
        if mcu.family != "micropython":
            log.warning(
                f"Skipping {mcu.family} {mcu.port} {mcu.board} on {mcu.serialport} as it is a MicroPython firmware"
            )
            continue
        board_firmwares = find_firmware(
            fw_folder=fw_folder,
            board=mcu.board,
            version=target_version,
            port=mcu.port,
            selector=selector,
        )

        if not board_firmwares:
            log.error(f"No {target_version} firmware found for {mcu.board} on {mcu.serialport}.")
            continue
        if len(board_firmwares) > 1:
            log.debug(f"Multiple {target_version} firmwares found for {mcu.board} on {mcu.serialport}.")

        # just use the last firmware
        fw_info = board_firmwares[-1]
        log.info(f"Found {target_version} firmware {fw_info['filename']} for {mcu.board} on {mcu.serialport}.")
        wl.append((mcu, fw_info))
    return wl


def enter_bootloader(mcu: MPRemoteBoard, timeout: int = 10, wait_after: int = 2):
    """Enter the bootloader mode for the board"""
    log.info(f"Entering bootloader on {mcu.board} on {mcu.serialport}")
    mcu.run_command("bootloader", timeout=timeout)
    time.sleep(wait_after)


# TODO:
# flash from some sort of queue to allow different images to be flashed to the same board
#  - flash variant 1
#  - stub variant 1
#  - flash variant 2
#  - stub variant 2
#
# JIT download / download any missing firmwares based on the detected boards
