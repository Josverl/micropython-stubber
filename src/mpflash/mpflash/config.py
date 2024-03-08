"""centralized configuration for mpflash"""

from typing import List


class MPtoolConfig:
    """Centralized configuration for mpflash"""

    quiet: bool = False
    ignore_ports: List[str] = []


config = MPtoolConfig()
