# sourcery skip: snake-case-functions
"""Flash a MCU with a UF2 bootloader on Windows"""

from __future__ import annotations

import time
from pathlib import Path

import psutil
from rich.progress import track

from .flash_uf2_boardid import get_board_id


def wait_for_UF2_windows(s_max: int = 10):
    """Wait for the MCU to mount as a drive"""
    if s_max < 1:
        s_max = 10
    destination = ""
    for _ in track(range(s_max), description="Waiting for mcu to mount as a drive", transient=True):
        # log.info(f"Waiting for mcu to mount as a drive : {n} seconds left")
        drives = [drive.device for drive in psutil.disk_partitions()]
        for drive in drives:
            try:
                if Path(drive, "INFO_UF2.TXT").exists():
                    board_id = get_board_id(Path(drive))  # type: ignore
                    destination = Path(drive)
                    break
            except OSError:
                pass
        if destination:
            break
        time.sleep(1)
    return destination
