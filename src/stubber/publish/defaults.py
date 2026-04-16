"""Build and packaging defaults for stubber"""

from typing import Dict, List

from loguru import logger as log
from mpflash.versions import V_PREVIEW, clean_version
from stubber.utils.config import CONFIG

# The default board for the ports modules documented with base name only
# as the MicroPython BOARD naming convention has changed over time there are different options to try
# (newer to older)

DEFAULT_BOARDS: Dict[str, List[str]] = {
    "stm32": ["PYBV11", ""],
    "esp32": ["ESP32_GENERIC", "GENERIC", ""],  #  "GENERIC_SPIRAM",
    "esp8266": ["ESP8266_GENERIC", "GENERIC", ""],
    "rp2": ["RPI_PICO_W", "RPI_PICO", "PICO", ""],
    "samd": ["SEEED_WIO_TERMINAL", ""],
    "mimxrt": ["SEEED_ARCH_MIX", ""],
    "unix": ["standard", ""],
    "windows": ["standard", ""],
    "webassembly": ["pyscript", "standard", ""],
}

GENERIC_L = "generic"
"generic lowercase"
GENERIC_U = "GENERIC"
"GENERIC uppercase"
GENERIC = {GENERIC_L, GENERIC_U}
"GENERIC eithercase"

DEFAULT_L = "default"
"default lowercase"
DEFAULT_U = "DEFAULT"
"DEFAULT uppercase"
DEFAULT = {DEFAULT_L, DEFAULT_U}
"DEFAULT eithercase"

DEFAULT_ALIASES = GENERIC | DEFAULT
"Accepted aliases for selecting a per-port default board"


def default_board(port: str, version=V_PREVIEW) -> str:  # sourcery skip: assign-if-exp
    """Return the default board for the given version and port"""
    ver_flat = clean_version(version, flat=True)
    log.info(f"Resolving default board for port='{port}', version='{version}' (flat='{ver_flat}')")
    if port in DEFAULT_BOARDS:
        for board in DEFAULT_BOARDS[port]:
            base = f"micropython-{ver_flat}-{port}-{board}" if board else f"micropython-{ver_flat}-{port}"
            # check if we have a (merged)stub for this version and port
            merged_candidate = CONFIG.stub_path / f"{base}-merged"
            base_candidate = CONFIG.stub_path / base
            merged_exists = merged_candidate.exists()
            base_exists = base_candidate.exists()
            log.info(
                f"Checking board candidate '{board or '<no-board>'}' for {port} {version}: "
                f"merged={merged_exists} ({merged_candidate}), "
                f"base={base_exists} ({base_candidate})"
            )
            if merged_exists or base_exists:
                log.info(f"Default board for {port} {version} is '{board}'")
                return board
        # fallback to first listed board
        log.info(f"Fallback default board for {port} {version} is '{DEFAULT_BOARDS[port][0]}'")
        return DEFAULT_BOARDS[port][0]
    # fallback to generic
    return GENERIC_U
