"""centralized configuration for mptool"""

from typing import List


class MPtoolConfig:
    ignore_ports: List[str] = []


config = MPtoolConfig()
