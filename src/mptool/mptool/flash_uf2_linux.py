from __future__ import annotations
from pathlib import Path
import subprocess
import sys
import time
from loguru import logger as log

from typing import List
from .uf2_boardid import get_board_id

glb_dismount_me : List[UF2Disk] = []

class UF2Disk:
    """Info to support mounting and unmounting of UF2 drives on linux"""
    device_path: str
    label: str
    mountpoint: str

    def __repr__(self):
        return repr(self.__dict__)

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
    'tran': 'usb',
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
        subprocess.run(["pmount",disk.device_path,  disk.mountpoint ])
        log.info(f"Mounted {disk.label} at {disk.mountpoint}")
        glb_dismount_me.append(disk)
    else:
        log.warning(f"{disk.label} already mounted at {disk.mountpoint}")

def pumount(disk: UF2Disk):
    """
    Unmount a UF2 drive
    """
    if sys.platform != "linux":
        log.error("pumount only works on Linux")
        return
    if disk.mountpoint:
        subprocess.run(["pumount", disk.mountpoint]) # ), f"/media/{disk.label}"])
        log.info(f"Unmounted {disk.label} from {disk.mountpoint}")
        disk.mountpoint = f""
    else:
        log.warning(f"{disk.label} already dismounted")

def dismount_uf2():
    global glb_dismount_me
    for disk in glb_dismount_me:
        pumount(disk)
    glb_dismount_me = []

def wait_for_UF2_linux():
    destination = ""
    wait = 10
    uf2_drives = []
    while not destination and wait > 0:
        log.info(f"Waiting for mcu to mount as a drive : {wait} seconds left")
        uf2_drives += list(get_uf2_drives())
        for drive in get_uf2_drives():
            pmount(drive)
            time.sleep(1)
            if Path(drive.mountpoint, "INFO_UF2.TXT").exists():
                board_id = get_board_id(Path(drive.mountpoint)) # type: ignore
                destination = Path(drive.mountpoint)
                break
        time.sleep(1)
        wait -= 1
    return destination