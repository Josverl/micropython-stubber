#!/usr/bin/env python3
"""
Collect modules and python stubs from other projects
"""
# Copyright (c) 2020 Jos Verlinde
# MIT license

import glob
import os
import shutil
import subprocess

import basicgit as git
import freezer_mpy
import freezer_lobo

import logging
log = logging.getLogger(__name__)

STUB_FOLDER = './all-stubs'

# todo: add frozen modules for :
# import freezer_pycopy
# import freezer_pycom

def make_stub_files(stub_path, levels: int = 1):
    "generate typeshed files for all scripts in a folder"
    level = ""
    # make_sub_files.py only does one folder level at a time
    # so lets try 7 levels /** ,  /**/** , etc
    for i in range(levels):
        cmd = "py ./src/make_stub_files.py -c ./src/make_stub_files.cfg -u {}{}/*.py".format(stub_path, level)
        log.debug("level {} : {}".format(i+1, cmd))
        os.system(cmd)
        level = level + '/**'

#def pip_download(requirements, path:str):
def get_cpython(requirements, stub_path=None):
    "Download MicroPython compatibility modules"
    if not stub_path:
        stub_path = './stubs/cpython-core'
    # use pip to dowload requirements file to build folder in one go
    #   pip install --no-compile --no-cache-dir --target ./scratch/test --upgrade -r ./src/microcpython.txt
    build_path = os.path.abspath("./build")
    os.makedirs(stub_path, exist_ok=True)
    os.makedirs(build_path, exist_ok=True)
    try:
        subprocess.run(["pip", "install", "--target", build_path, "-r", requirements, "--no-cache-dir", "--no-compile", "--upgrade"], capture_output=False, check=True)
        # copy *.py files in build folder to stub_path
        for filename in glob.glob(os.path.join(build_path, "*.py")):
            log.info("pipped : {}".format(filename))
            try:
                shutil.copy2(filename, stub_path)
            except OSError as e:
                log.exception(e)
    except OSError as e:
        log.error("An error occurred while trying to run pip to dowload the MicroPython compatibility modules from PyPi: {}".format(e))
    finally:
        # remove build folder
        shutil.rmtree(build_path, ignore_errors=True)

def flat_version(version: str):
    "Turn 'v1.2.3' into '1_2_3' "
    return version.replace('v', '').replace('.', '_')

def clean_version(version:str, build:bool = False):
    "omit the commit hash from the git tag"
    # 'v1.13-103-gb137d064e' --> 'v1.13-103'
    nibbles = version.split('-')
    if len(nibbles) == 1:
        return version
    elif build:
        return '-'.join(version.split('-')[0:-1])
    else:
       return '-'.join((version.split('-')[0], 'nightly'))

def get_all():
    "get all frozen modules for the current version of micropythin"

    #todo: checkout/check specific version of micropython
    mpy_path = '../micropython'
    version = clean_version(git.get_tag(mpy_path))
    
    if version:
        log.info("found micropython version : {}".format(version))
        # folder/{family}_{version}_frozen
        stub_path = '{}/{}_{}_frozen'.format(STUB_FOLDER,'mpy',flat_version(version))
        freezer_mpy.get_frozen(stub_path, mpy_path, lib_path='../micropython-lib')
    else:
        log.warning('Unable to find the micropython repo in folder : {}'.format(mpy_path))


    # get_cpython(stub_path='./stubs/cpython-core', requirements='./src/micro-cpython.txt')

    # freezer_lobo.get_frozen(stub_path='./stubs/esp32_LoBo_3_2_24_Frozen')

    # now generate typeshed files for all scripts
    log.info("Generate type hint files (pyi) in folder: {}".format(STUB_FOLDER))
    make_stub_files(STUB_FOLDER, levels=7)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(name)-10s %(levelname)-8s:%(message)s')
#                        format='%(name)-10s %(funcName)-20s %(levelname)-8s:%(message)s')
    get_all()
    # get_cpython(stub_path='./stubs/cpython-core', requirements='./src/micro-cpython.txt')
