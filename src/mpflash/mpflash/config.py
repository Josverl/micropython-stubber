"""centralized configuration for mpflash"""

from pathlib import Path
from typing import List

import pkg_resources
import platformdirs


def get_version():
    name = __package__ or "mpflash"
    try:
        return pkg_resources.get_distribution(name).version
    except pkg_resources.DistributionNotFound:
        return "Package not found"


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
__version__ = get_version()
