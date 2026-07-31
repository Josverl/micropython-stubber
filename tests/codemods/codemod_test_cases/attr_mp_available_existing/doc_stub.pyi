# fmt: off
"""
Reference stub with a `# mp_available` class attribute already present in target
"""

from typing import Dict, List

class ESPNow:
    """ESPNow singleton."""

    # mp_available
    peers_table: Dict[bytes, List[int]] = ...
    """A reference to the peer device table."""
    def __init__(self) -> None: ...
