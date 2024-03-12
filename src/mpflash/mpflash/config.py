"""centralized configuration for mpflash"""

import platformdirs

from typing import List
from pathlib import Path


class MPtoolConfig:
    """Centralized configuration for mpflash"""

    quiet: bool = False
    ignore_ports: List[str] = []
    firmware_folder: Path = platformdirs.user_downloads_path() / "firmware"


config = MPtoolConfig()
