from pathlib import Path

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
