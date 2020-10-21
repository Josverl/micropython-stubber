#!/usr/bin/env python3
"""
Collect modules and python stubs from the Loboris MicroPython source project
"""
# pylint: disable= line-too-long
# Copyright (c) 2020 Jos Verlinde
# MIT license
import logging
import downloader

family = 'lobo'
log = logging.getLogger(__name__)
# log.setLevel(level=logging.DEBUG)

def get_frozen(stub_path, *, repo=None):
    "Loboris frozen modules"
    if not stub_path:
        stub_path = './stubs/esp32_lobo_frozen'

    if not repo:
        repo = 'https://raw.githubusercontent.com/loboris/MicroPython_ESP32_psRAM_LoBo/master/MicroPython_BUILD/components/micropython/esp32/modules/{}'

    frozen_modules = ["README.md", "ak8963.py", "freesans20.py", "functools.py", "logging.py", "microWebSocket.py", "microWebSrv.py", "microWebTemplate.py", "mpu6500.py", "mpu9250.py", "pye.py", "ssd1306.py", "tpcalib.py", "upip.py",
                      "upip_utarfile.py", "upysh.py", "urequests.py", "writer.py"]
    #download
    downloader.download_files(repo, frozen_modules, stub_path)


if __name__ == "__main__":
    # just run a quick test
    logging.basicConfig(format='%(levelname)-8s:%(message)s',level=logging.INFO)
    get_frozen(stub_path='./scratch/esp32_lobo_frozen')
