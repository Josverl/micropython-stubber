"""centralized configuration for mpflash"""

import os
from importlib.metadata import version
from pathlib import Path
from typing import List

import platformdirs

from mpflash.logger import log


def get_version():
    name = __package__ or "mpflash"
    return version(name)


class MPtoolConfig:
    """Centralized configuration for mpflash"""

    quiet: bool = False
    verbose: bool = False
    usb: bool = False
    ignore_ports: List[str] = []
    firmware_folder: Path = platformdirs.user_downloads_path() / "firmware"
    # test options specified on the commandline
    tests: List[str] = []
    _interactive: bool = True

    @property
    def interactive(self):
        # No interactions in CI
        if os.getenv("GITHUB_ACTIONS") == "true":
            log.warning("Disabling interactive mode in CI")
            return False
        return self._interactive

    @interactive.setter
    def interactive(self, value: bool):
        self._interactive = value


config = MPtoolConfig()
__version__ = get_version()
