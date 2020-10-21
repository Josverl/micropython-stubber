#!/usr/bin/env python3
"""
Collect modules and python stubs from the Loboris MicroPython source project
"""
# pylint: disable= line-too-long
# Copyright (c) 2020 Jos Verlinde
# MIT license
import os
import glob
import json
import logging
import downloader
import utils

family = 'loboris'
log = logging.getLogger(__name__)
# log.setLevel(level=logging.DEBUG)

def get_frozen(stub_path, *, repo=None, version = '3.2.24'):
    "Loboris frozen modules"
    if not stub_path:
        stub_path = './stubs/esp32_lobo_frozen'

    if not repo:
        repo = 'https://raw.githubusercontent.com/loboris/MicroPython_ESP32_psRAM_LoBo/master/MicroPython_BUILD/components/micropython/esp32/modules/{}'

    frozen_modules = ["README.md", "ak8963.py", "freesans20.py", "functools.py", "logging.py", "microWebSocket.py", "microWebSrv.py", "microWebTemplate.py", "mpu6500.py", "mpu9250.py", "pye.py", "ssd1306.py", "tpcalib.py", "upip.py",
                      "upip_utarfile.py", "upysh.py", "urequests.py", "writer.py"]
    #download
    downloader.download_files(repo, frozen_modules, stub_path)
    # build modules.json
    mod_manifest = utils.manifest(machine=family, sysname='lobo', version=version)
    for filename in glob.glob(os.path.join(stub_path, "*.py")):
        f_name, f_ext = os.path.splitext(os.path.basename(filename))
        mod_manifest['modules'].append({ "file": os.path.basename(filename), "module":f_name})
    #write the the module manifest 
    with open(stub_path+"/modules.json", "w") as outfile:
        json.dump(mod_manifest, outfile)


if __name__ == "__main__":
    # just run a quick test
    logging.basicConfig(format='%(levelname)-8s:%(message)s',level=logging.INFO)
    get_frozen(stub_path='./scratch/esp32_lobo_frozen', version='3.2.24')
