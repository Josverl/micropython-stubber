#################################################
# test the fwid naming on the different platforms
#################################################

import pytest

from collections import namedtuple
from typing import Any, Optional, Tuple

pytestmark = [pytest.mark.stubber]

## os.uname()
# import os; print(os.uname())

UName = namedtuple("uname", "sysname nodename release version machine")
# Lobo
lobo = UName(
    sysname="esp32_LoBo",
    nodename="esp32_LoBo",
    release="3.2.24",
    version="ESP32_LoBo_v3.2.24 on 2018-09-06",
    machine="ESP32 board with ESP32",
)
lobo_bt_ram = UName(
    sysname="esp32_LoBo",
    nodename="esp32_LoBo",
    release="3.2.24",
    version="ESP32_LoBo_v3.2.24 on 2018-09-06",
    machine="ESP32&psRAM board with ESP32",
)

# mpy 113
mpy_v1_13_SPI = UName(
    sysname="esp32",
    nodename="esp32",
    release="1.13.0",
    version="v1.13 on 2020-09-02",
    machine="ESP32 module (spiram) with ESP32",
)
mpy_v1_13_build = UName(
    sysname="esp32",
    nodename="esp32",
    release="1.13.0",
    version="v1.13-103-gb137d064e on 2020-10-09",
    machine="ESP32 module (spiram) with ESP32",
)
mpy_v1_10 = UName(
    sysname="esp32",
    nodename="esp32",
    release="1.10.0",
    version="v1.10 on 2019-01-25",
    machine="ESP32 module with ESP32",
)

mpy_v1_9_4 = UName(
    sysname="esp32",
    nodename="esp32",
    release="1.9.4",
    version="v1.9.4 on 2018-05-11",
    machine="ESP32 module with ESP32",
)

mpy_v1_11_8_esp8266 = UName(
    sysname="esp8266",
    nodename="esp8266",
    release="2.2.0-dev(9422289)",
    version="v1.11-8-g48dcbbe60 on 2019-05-29",
    machine="ESP module with ESP8266",
)
mpy_v1_11_esp8266 = UName(
    sysname="esp8266",
    nodename="esp8266",
    release="2.2.0-dev(9422289)",
    version="v1.11 on 2019-05-29",
    machine="ESP module with ESP8266",
)
mpy_v1_17_esp8266_GEN = UName(
    sysname="esp8266",
    nodename="esp8266",
    release="2.0.0(5a875ba)",
    version="v1.17 on 2021-09-02",
    machine="ESP module with ESP8266",
)
uname_mpy_v1_22_esp32_GEN = UName(
    sysname="esp32",
    nodename="esp32",
    release="1.22.0",
    version="v1.22.0 on 2023-12-27",
    machine="Generic ESP32 module with SPIRAM with ESP32",
)

pyb1_v1_13_PYB11 = UName(
    sysname="pyboard",
    nodename="pyboard",
    release="1.13.0",
    version="v1.13-95-g0fff2e03f on 2020-10-03",
    machine="PYBv1.1 with STM32F405RG",
)

rp2_v1_18 = UName(
    sysname="rp2",
    nodename="rp2",
    release="1.18.0",
    version="v1.18-95-g0fff2e03f on 2020-10-03",
    machine="rp2v1.1 with ????",
)


# TODO: add support for -Latest
# ('micropython-1.13-latest-esp32', 'micropython', 'esp32', mpy_v1_13_build),


class MP_Implementation:
    """Mock sys.implementation for MicroPython"""

    name: str
    version: Tuple
    _machine: Optional[str]  # newer MicroPython versions have this attribute
    _mpy: Optional[int]  #  MicroPython >= 1.11

    # Define __getattr__, as the documentation states:
    # > sys.implementation may contain additional attributes specific to the Python implementation.
    # > These non-standard attributes must start with an underscore, and are not described here.
    def __getattr__(self, name: str) -> Any: ...

    def __init__(self, name: str, version: Tuple, *, _machine=None, _mpy=None):
        self.name = name
        self.version = version
        self._machine = _machine
        self._mpy = _mpy


fwid_test_cases = [
    # - expected firmware id
    # - patch input -  sys.implementation( name, version, _machine, _mpy)
    # - patch input -  sys.platform
    # - patch input -  sys.version (str)
    # - patch input -  os.uname stucture
    # - patch input -  array of modules to mock for firmware detection
    (
        "micropython-v1.9.4-esp32",
        MP_Implementation(name="micropython", version=(1, 9, 4)),
        "esp32",
        "",
        mpy_v1_9_4,
        [],
    ),
    (
        "micropython-v1.10-esp32",
        MP_Implementation(
            "micropython",
            (1, 10, 0),
        ),
        "esp32",
        "",
        mpy_v1_10,
        [],
    ),
    (
        "micropython-v1.13-preview-esp32",
        MP_Implementation(
            "micropython",
            (1, 13, 0),
        ),
        "esp32",
        "3.4.0",
        mpy_v1_13_build,
        [],
    ),
    (
        "micropython-v1.11-esp8266",
        MP_Implementation(
            "micropython",
            (1, 11, 0),
        ),
        "esp8266",
        "",
        mpy_v1_11_esp8266,
        [],
    ),
    (
        "micropython-v1.11-preview-esp8266",
        MP_Implementation(
            "micropython",
            (1, 11, 0),
        ),
        "esp8266",
        "",
        mpy_v1_11_8_esp8266,
        [],
    ),
    (
        "micropython-v1.17-esp8266",
        MP_Implementation(
            "micropython",
            (1, 17, 0),
        ),
        "esp8266",
        "",
        mpy_v1_17_esp8266_GEN,
        [],
    ),
    # mpy pyb1
    (
        "micropython-v1.13-preview-stm32",
        MP_Implementation(
            "micropython",
            (1, 13, 0),
        ),
        "pyb1",
        "",
        pyb1_v1_13_PYB11,
        [],
    ),
    # RP2
    (
        "micropython-v1.18-preview-rp2",
        MP_Implementation(
            "micropython",
            (1, 18, 0),
        ),
        "rp2",
        "",
        UName(
            sysname="rp2",
            nodename="rp2",
            release="1.18.0",
            version="v1.18-g0fff2e03f on 2020-10-03",
            machine="Raspberry Pi Pico with RP2040",
        ),
        [],
    ),
    # ev3_pybricks_1_0_0
    (
        "ev3-pybricks-v2.0.0-unix",
        MP_Implementation(
            "",
            (2, 0, 0),
        ),
        "linux",
        "",
        UName(
            machine="ev3",
            nodename="ev3",
            release=None,
            sysname="ev3",
            version=None,
        ),
        ["pybricks", "pybricks.hubs"],
    ),
    # ev3_pybricks_2_0_0
    # TODO: Mock import from package
    # ModuleNotFoundError: No module named 'pybricks.hubs'; 'pybricks' is not a package
    # (
    #     "ev3-pybricks-v2.0.0-linux",
    #     "",
    #     "linux",
    #     UName(machine="ev3", nodename="ev3", release=None, sysname="ev3", version=None),
    #     ["pybricks", "hubs" "pybricks.hubs"],
    # ),
    # pycopy
    (
        "pycopy-v1.2.3-stm32",
        MP_Implementation(
            "pycopy",
            (1, 2, 3),
        ),
        "pyb1",
        "",
        UName(
            sysname="stm32",
            nodename="stm32",
            release="1.2.3-beta0",
            version="v1.2.3",
            machine="stm32 ????",
        ),
        ["pycopy"],
    ),
    # pycom
    (
        "pycom-v1.18.0-preview-esp32",
        MP_Implementation(
            "pycom",
            (1, 18, 0),
        ),
        "esp32",
        "",
        UName(
            sysname="esp32",
            nodename="esp32",
            release="1.18.0",
            version="v1.18-95-g0fff2e03f on 2020-10-03",
            machine="WiPy module with ESP32",
        ),
        ["pycom"],
    ),
    # 1.19.1
    (
        "micropython-v1.19.1-preview-rp2",
        MP_Implementation("micropython", (1, 19, 1)),
        "rp2",
        "",
        UName(
            sysname="rp2",
            nodename="rp2",
            release="1.19.1",
            version="v1.19.1-721-gd5181034f on 2022-11-28",
            machine="Raspberry Pi Pico W with RP2040",
        ),
        [],
    ),
    (
        "micropython-v1.19.1-rp2",
        MP_Implementation("micropython", (1, 19, 1)),
        "rp2",
        "",
        UName(
            sysname="rp2",
            nodename="rp2",
            release="1.19.1",
            version="67fac4e on 2023-02-16 (GNU 9.2.1 MinSizeRel)",
            machine="Pimoroni Pico LiPo 16MB with RP2040",
        ),
        [],
    ),
    # version 1.22
    (
        # using uname (old)
        "micropython-v1.22.0-esp32",
        MP_Implementation("micropython", (1, 22, 0, "")),
        "esp32",
        "",
        uname_mpy_v1_22_esp32_GEN,
        [],
    ),
    (
        # using _machine and uname
        "micropython-v1.22.0-esp32",
        MP_Implementation("micropython", (1, 22, 0, ""), _machine="Generic ESP32 module with SPIRAM with ESP32"),
        "esp32",
        "",
        uname_mpy_v1_22_esp32_GEN,
        [],
    ),
    (
        # using _machine only (new)
        "micropython-v1.22.0-samd",
        MP_Implementation("micropython", (1, 22, 0, ""), _machine="Wio Terminal D51R with SAMD51P19A"),
        "samd",
        "",
        None,
        [],
    ),
    (
        # using _machine only (new)
        "micropython-v1.23.0-preview-samd",
        MP_Implementation("micropython", (1, 23, 0, "preview"), _machine="Wio Terminal D51R with SAMD51P19A"),
        "samd",
        "3.4.0; MicroPython v1.23.0-preview.6.g3d0b6276f on 2024-01-02",  # sys.version
        None,
        [],
    ),
]
