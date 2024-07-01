""" Flashing UF2 based MCU on macos"""

# sourcery skip: snake-case-functions
from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from rich.progress import track

from .boardid import get_board_id


def wait_for_UF2_macos(board_id: str, s_max: int = 10) -> Optional[Path]:
    """Wait for the MCU to mount as a drive"""
    if s_max < 1:
        s_max = 10
    destination = None
    for _ in track(
        range(s_max),
        description=f"Waiting for mcu to mount as a drive ({s_max}s)",
        transient=True,
        show_speed=False,
        refresh_per_second=1,
        total=s_max,
    ):
        vol_mounts = Path("/Volumes").iterdir()
        for vol in vol_mounts:
            try:
                if Path(vol, "INFO_UF2.TXT").exists():
                    this_board_id = get_board_id(Path(vol))
                    if not board_id or board_id.upper() in this_board_id.upper():
                        destination = Path(vol)
                        break
                    continue
            except OSError:
                pass
        if destination:
            break
        time.sleep(1)
    return destination
