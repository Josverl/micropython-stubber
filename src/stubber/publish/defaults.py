"""Build and packaging defaults for stubber"""

from typing import Dict, List

from mpflash.versions import V_PREVIEW, clean_version
from stubber.utils.config import CONFIG

# The default board for the ports modules documented with base name only
# as the MicroPython BOARD naming convention has changed over time there are different options to try
# (newer to older)

DEFAULT_BOARDS: Dict[str, List[str]] = {
    "stm32": ["PYBV11", ""],
    "esp32": ["ESP32_GENERIC", "GENERIC", ""],  #  "GENERIC_SPIRAM",
    "esp8266": ["ESP8266_GENERIC", "GENERIC", ""],
    "rp2": ["RPI_PICO", "PICO", ""],
    "samd": ["SEEED_WIO_TERMINAL", ""],
}

GENERIC_L = "generic"
"generic lowercase"
GENERIC_U = "GENERIC"
"GENERIC uppercase"
GENERIC = {GENERIC_L, GENERIC_U}
"GENERIC eithercase"


def default_board(port: str, version=V_PREVIEW) -> str:  # sourcery skip: assign-if-exp
    """Return the default board for the given version and port"""
    ver_flat = clean_version(version, flat=True)
    if port in DEFAULT_BOARDS:
        for board in DEFAULT_BOARDS[port]:
            base = f"micropython-{ver_flat}-{port}-{board}" if board else f"micropython-{ver_flat}-{port}"
            # check if we have a (merged)stub for this version and port
            if (CONFIG.stub_path / f"{base}-merged").exists() or (CONFIG.stub_path / base).exists():
                return board
        # fallback to first listed board
        return DEFAULT_BOARDS[port][0]
    # fallback to generic
    return GENERIC_U
