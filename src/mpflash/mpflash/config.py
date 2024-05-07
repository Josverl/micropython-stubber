"""centralized configuration for mpflash"""

from pathlib import Path
from typing import List

import platformdirs


class MPtoolConfig:
    """Centralized configuration for mpflash"""

    quiet: bool = False
    verbose: bool = False
    ignore_ports: List[str] = []
    interactive: bool = True
    firmware_folder: Path = platformdirs.user_downloads_path() / "firmware"
    # test options specified on the commandline
    tests: List[str] = []


config = MPtoolConfig()
