#!/usr/bin/env python3
"""
Collect modules and python stubs from the Loboris MicroPython source project and stores them in the all_stubs folder
The all_stubs folder should be mapped/symlinked to the micropython_stubs/stubs repo/folder
"""

# pylint: disable= line-too-long
# Copyright (c) 2020 Jos Verlinde
# MIT license
from pathlib import Path
from typing import Optional

from . import downloader, utils
from .utils.config import CONFIG

FAMILY = "loboris"
PORT = "esp32_lobo"


def get_frozen(stub_path: Optional[Path] = None, *, repo: Optional[str] = None, version="3.2.24"):
    "Download Loboris frozen modules direct from github repo"
    if stub_path is None:
        stub_path = CONFIG.stub_path / "{}-{}-frozen".format(FAMILY, utils.clean_version(version, flat=True))
    else:
        stub_path = Path(stub_path)

    if not repo:
        repo = "https://raw.githubusercontent.com/loboris/MicroPython_ESP32_psRAM_LoBo/master/MicroPython_BUILD/components/micropython/esp32/modules/{}"

    frozen_modules = [
        "README.md",
        "ak8963.py",
        "freesans20.py",
        "functools.py",
        "logging.py",
        "microWebSocket.py",
        "microWebSrv.py",
        "microWebTemplate.py",
        "mpu6500.py",
        "mpu9250.py",
        "pye.py",
        "ssd1306.py",
        "tpcalib.py",
        #        "upip.py",
        #        "upip_utarfile.py",
        #        "upysh.py",
        "urequests.py",
        "writer.py",
    ]
    # download
    downloader.download_files(repo, frozen_modules, stub_path)
    # make a manifest
    utils.make_manifest(
        stub_path,
        FAMILY,
        port="esp32",
        version=version,
        stubtype="frozen",
    )
