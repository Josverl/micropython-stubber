""" Flashing UF2 based MCU on macos"""

# sourcery skip: snake-case-functions
from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from rich.progress import track



def wait_for_UF2_macos(s_max: int = 10) -> Optional[Path]:
    """Wait for the MCU to mount as a drive"""
    if s_max < 1:
        s_max = 10
    destination = None
    for _ in track(
        range(s_max), description="Waiting for mcu to mount as a drive", transient=True, refresh_per_second=2
    ):
        # log.info(f"Waiting for mcu to mount as a drive : {n} seconds left")
        vol_mounts = Path("/Volumes").iterdir()
        for vol in vol_mounts:
            try:
                if Path(vol, "INFO_UF2.TXT").exists():
                    destination = Path(vol)
                    break
            except OSError:
                pass
        if destination:
            break
        time.sleep(1)
    return destination
