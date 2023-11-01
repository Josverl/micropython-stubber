"""Build and packaging defaults for stubber"""
from typing import Dict

# The default board for the ports modules documented with base name only
# ESP32-GENERIC is currently hardcoded
DEFAULT_BOARDS: Dict[str, str] = {
    "stm32": "PYBV11",
    "esp32": "GENERIC",
    "esp8266": "GENERIC",
    "rp2": "PICO",
    "samd": "SEEED_WIO_TERMINAL",
}

GENERIC_L = "generic"
"generic lowercase"
GENERIC_U = "GENERIC"
"GENERIC uppercase"
GENERIC = {GENERIC_L, GENERIC_U}
"GENERIC eithercase"


def default_board(port: str) -> str:  # sourcery skip: assign-if-exp
    """Return the default board for the given port"""
    if port in DEFAULT_BOARDS:
        return DEFAULT_BOARDS[port]
    else:
        return GENERIC_U
