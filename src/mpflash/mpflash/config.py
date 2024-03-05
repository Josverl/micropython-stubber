"""centralized configuration for mpflash"""

from typing import List


class MPtoolConfig:
    ignore_ports: List[str] = []


config = MPtoolConfig()
