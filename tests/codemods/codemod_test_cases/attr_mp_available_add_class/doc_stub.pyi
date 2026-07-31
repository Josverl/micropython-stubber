# fmt: off
"""
Reference stub with a `# mp_available` class attribute
"""

from typing import Dict, List

class ESPNow:
    """ESPNow singleton."""

    # mp_available
    # ESP32-only when MICROPY_PY_ESPNOW_RSSI is enabled.
    peers_table: Dict[bytes, List[int]] = ...
    """A reference to the peer device table."""
    def __init__(self) -> None: ...
    def active(self, flag: bool) -> bool: ...
