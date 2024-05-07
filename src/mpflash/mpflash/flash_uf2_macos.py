""" Flashing UF2 based MCU on macos"""

# sourcery skip: snake-case-functions
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import List

from loguru import logger as log
from rich.progress import track

from .flash_uf2_boardid import get_board_id
from .uf2disk import UF2Disk


def get_uf2_drives():
    """
    Get a list of all the (un)mounted UF2 drives
    """
    if sys.platform != "linux":
        log.error("pumount only works on Linux")
        return
    # import blkinfo only on linux
    from blkinfo import BlkDiskInfo

    myblkd = BlkDiskInfo()
    filters = {
        "tran": "usb",
    }
    usb_disks = myblkd.get_disks(filters)
    for disk in usb_disks:
        if disk["fstype"] == "vfat":
            uf2_part = disk
            # unpartioned usb disk or partition (e.g. /dev/sdb )
            # SEEED WIO Terminal is unpartioned
            # print( json.dumps(uf2_part, indent=4))
            uf2 = UF2Disk()
            uf2.device_path = "/dev/" + uf2_part["name"]
            uf2.label = uf2_part["label"]
            uf2.mountpoint = uf2_part["mountpoint"]
            yield uf2
        elif disk["type"] == "disk" and disk.get("children") and len(disk.get("children")) > 0:
            if disk.get("children")[0]["type"] == "part" and disk.get("children")[0]["fstype"] == "vfat":
                uf2_part = disk.get("children")[0]
                # print( json.dumps(uf2_part, indent=4))
                uf2 = UF2Disk()
                uf2.device_path = "/dev/" + uf2_part["name"]
                uf2.label = uf2_part["label"]
                uf2.mountpoint = uf2_part["mountpoint"]
                yield uf2


def wait_for_UF2_macos(s_max: int = 10):
    destination = ""
    wait = 10
    uf2_drives = []
    # while not destination and wait > 0:
    for _ in track(
        range(s_max), description="Waiting for mcu to mount as a drive", transient=True, refresh_per_second=2
    ):
        # log.info(f"Waiting for mcu to mount as a drive : {wait} seconds left")
        uf2_drives += list(get_uf2_drives())
        for drive in get_uf2_drives():
            time.sleep(1)
            try:
                if Path(drive.mountpoint, "INFO_UF2.TXT").exists():
                    board_id = get_board_id(Path(drive.mountpoint))  # type: ignore
                    destination = Path(drive.mountpoint)
                    break
            except PermissionError:
                log.debug(f"Permission error on {drive.mountpoint}")
                continue
        if destination:
            break
        time.sleep(1)
        wait -= 1
    return destination
