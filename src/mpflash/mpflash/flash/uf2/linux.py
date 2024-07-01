""" Flashing UF2 based MCU on Linux"""

# sourcery skip: snake-case-functions
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import List

from loguru import logger as log
from rich.progress import track

from .boardid import get_board_id
from .uf2disk import UF2Disk

glb_dismount_me: List[UF2Disk] = []


def get_uf2_drives():
    """
    Get a list of all the (un)mounted UF2 drives
    """
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


def pmount(disk: UF2Disk):
    """
    Mount a UF2 drive if there is no mountpoint yet.
    """
    global glb_dismount_me
    if not disk.mountpoint:
        if not disk.label:
            disk.label = "UF2BOOT"
        disk.mountpoint = f"/media/{disk.label}"
        # capture error if pmount is not installed
        try:
            subprocess.run(["pmount", disk.device_path, disk.mountpoint])
        except FileNotFoundError:
            log.error("pmount not found, please install it using 'sudo apt install pmount'")
            return
        log.debug(f"Mounted {disk.label} at {disk.mountpoint}")
        glb_dismount_me.append(disk)
    else:
        log.trace(f"\n{disk.label} already mounted at {disk.mountpoint}")


def pumount(disk: UF2Disk):
    """
    Unmount a UF2 drive
    """
    if sys.platform != "linux":
        log.error("pumount only works on Linux")
        return
    if disk.mountpoint:
        subprocess.run(["pumount", disk.mountpoint])  # ), f"/media/{disk.label}"])
        log.info(f"Unmounted {disk.label} from {disk.mountpoint}")
        disk.mountpoint = f""
    else:
        log.warning(f"{disk.label} already dismounted")


def dismount_uf2_linux():
    global glb_dismount_me
    for disk in glb_dismount_me:
        pumount(disk)
    glb_dismount_me = []


def wait_for_UF2_linux(board_id: str, s_max: int = 10):
    destination = ""
    wait = 10
    uf2_drives = []
    # while not destination and wait > 0:
    for _ in track(
        range(s_max),
        description=f"Waiting for mcu to mount as a drive ({s_max}s)",
        transient=True,
        show_speed=False,
        refresh_per_second=1,
        total=s_max,
    ):
        uf2_drives += list(get_uf2_drives())
        for drive in get_uf2_drives():
            pmount(drive)
            time.sleep(1)
            try:
                if Path(drive.mountpoint, "INFO_UF2.TXT").exists():
                    this_board_id = get_board_id(Path(drive.mountpoint))
                    if not board_id or board_id.upper() in this_board_id.upper():
                        # is it the correct board?
                        destination = Path(drive.mountpoint)
                        break
                    continue
            except PermissionError:
                log.debug(f"Permission error on {drive.mountpoint}")
                continue
        if destination:
            break
        time.sleep(1)
        wait -= 1
    return destination
