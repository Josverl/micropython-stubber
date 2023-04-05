#################################################
# test the fwid naming on the different platforms
#################################################


from collections import namedtuple

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

mpy_v1_11_8_esp8622 = UName(
    sysname="esp8266",
    nodename="esp8266",
    release="2.2.0-dev(9422289)",
    version="v1.11-8-g48dcbbe60 on 2019-05-29",
    machine="ESP module with ESP8266",
)
mpy_v1_11_esp8622 = UName(
    sysname="esp8266",
    nodename="esp8266",
    release="2.2.0-dev(9422289)",
    version="v1.11 on 2019-05-29",
    machine="ESP module with ESP8266",
)
mpy_v1_17_esp8622_GEN = UName(
    sysname="esp8266",
    nodename="esp8266",
    release="2.0.0(5a875ba)",
    version="v1.17 on 2021-09-02",
    machine="ESP module with ESP8266",
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
fwid_test_cases = [
    # - expected firmware id
    # - patch input -  sys.implementation.name
    # - patch input -  sys.implementation.version
    # - patch input -  sys.platform
    # - patch input -  sys.os.uname stucture
    # - patch input -  array of modules to mock for firmware detection
    # mpy esp32
    ("micropython-v1.9.4-esp32-GENERIC", "micropython", (1, 9, 4), "esp32", mpy_v1_9_4, []),
    ("micropython-v1.10-esp32-GENERIC", "micropython", (1, 10, 0), "esp32", mpy_v1_10, []),
    ("micropython-v1.13-103-esp32-GENERIC_SPIRAM", "micropython", (1, 13, 0), "esp32", mpy_v1_13_build, []),
    # mpy esp8622
    ("micropython-v1.11-esp8622-GENERIC", "micropython", (1, 11, 0), "esp8622", mpy_v1_11_esp8622, []),
    ("micropython-v1.11-8-esp8622-GENERIC", "micropython", (1, 11, 0), "esp8622", mpy_v1_11_8_esp8622, []),
    ("micropython-v1.17-esp8622-GENERIC", "micropython", (1, 17, 0), "esp8622", mpy_v1_17_esp8622_GEN, []),
    # mpy pyb1
    ("micropython-v1.13-95-stm32-PYBV11", "micropython", (1, 13, 0), "pyb1", pyb1_v1_13_PYB11, []),
    # RP2
    (
        "micropython-v1.18-rp2",
        "micropython",
        (1, 18, 0),
        "rp2",
        UName(
            sysname="rp2",
            nodename="rp2",
            release="1.18.0",
            version="v1.18-g0fff2e03f on 2020-10-03",
            machine="rp2v1.1 with ????",
        ),
        [],
    ),
    (
        "micropython-v1.19.1-rp2-PIMORONI_PICOLIPO_16MB",
        "micropython",
        (1, 19, 1),
        "rp2",
        UName(
            sysname="rp2",
            nodename="rp2",
            release="1.19.1",
            version="67fac4e on 2023-02-16 (GNU 9.2.1 MinSizeRel)",
            machine="Pimoroni Pico LiPo 16MB with RP2040",
        ),
        [],
    ),
    # lobo
    # ("loboris-v3.2.24-esp32", "micropython", (3,2, 24), "esp32_LoBo", lobo, []),
    # ("loboris-v3.2.24-esp32", "micropython", (3,2, 24), "esp32_LoBo", lobo_bt_ram, []),
    # ev3_pybricks_1_0_0
    (
        "ev3-pybricks-v2.0.0-linux",
        "",
        (2, 0, 0),
        "linux",
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
        "pycopy-v1.2.3-beta0-stm32",
        "pycopy",
        (1, 2, 3),
        "pyb1",
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
        "pycom-v1.18.0-95-esp32",
        "pycom",
        (1, 18, 0),
        "esp32",
        UName(
            sysname="esp32",
            nodename="esp32",
            release="1.18.0",
            version="v1.18-95-g0fff2e03f on 2020-10-03",
            machine="WiPy module with ESP32",
        ),
        ["pycom"],
    ),
]
