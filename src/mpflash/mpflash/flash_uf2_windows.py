from __future__ import annotations
from pathlib import Path
import time
import psutil
from loguru import logger as log
from .uf2_boardid import get_board_id


def wait_for_UF2_windows():
    destination = ""
    wait = 10
    while not destination and wait > 0:
        log.info(f"Waiting for mcu to mount as a drive : {wait} seconds left")
        drives = [drive.device for drive in psutil.disk_partitions()]
        for drive in drives:
            if Path(drive, "INFO_UF2.TXT").exists():
                board_id = get_board_id(Path(drive))  # type: ignore
                destination = Path(drive)
                break
        time.sleep(1)
        wait -= 1
    return destination
