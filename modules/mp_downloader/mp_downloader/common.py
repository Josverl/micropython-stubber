from pathlib import Path
from typing import Dict, Union

PORT_FWTYPES = {
    "stm32": ".hex",
    "esp32": ".bin",
    "esp8266": ".bin",
    "rp2": ".uf2",
    "samd": ".uf2",
    "mimxrt": ".hex",
    "nrf": ".hex",
    "renesas-ra": ".hex",
}

DEFAULT_FW_PATH = Path.cwd() / "firmware"
# DEFAULT_FW_PATH = Path.home() / "mp_firmware"

FWInfo = Dict[str, Union[str, bool]]