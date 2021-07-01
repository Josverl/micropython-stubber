#!/usr/bin/env python3
"""
Collect modules and python stubs from other projects and stores them in the all_stubs folder
The all_stubs folder should be mapped/symlinked to the micropython_stubs/stubs repo/folder

 1) get cpython core modules
 2) get micropython frozen modules for the CURRENT checked out version
 2) get Loboris frozen modules (no longer maintained)

 4) Generate/update type hint files (pyi) for all stubs.

"""
# pylint: disable= line-too-long, W1202
# Copyright (c) 2020 Jos Verlinde
# MIT license
# pylint: disable= line-too-long
import logging

import basicgit as git

import utils
from utils import clean_version, stubfolder, flat_version

import get_cpython
import get_mpy
import get_lobo

# todo: add frozen modules for : pycopy
# import freezer_pycopy

log = logging.getLogger(__name__)

STUB_FOLDER = './all-stubs'

def get_all():
    "get all frozen modules for the current version of micropython"
    
    #
    get_cpython.get_core(stub_path=stubfolder('cpython_core'), requirements='./src/reqs-cpython-mpy.txt')

    mpy_path = '../micropython'
    version = clean_version(git.get_tag(mpy_path))

    if version:
        log.info("found micropython version : {}".format(version))
        # folder/{family}-{version}-frozen
        family = 'micropython'
        stub_path = stubfolder('{}-{}-frozen'.format(family, flat_version(version)))
        get_mpy.get_frozen(stub_path, version=version, mpy_path=mpy_path, lib_path='../micropython-lib')
    else:
        log.warning('Unable to find the micropython repo in folder : {}'.format(mpy_path))

    get_lobo.get_frozen(stub_path=STUB_FOLDER + '/loboris-esp32_lobo_3_2_24' + '-frozen')

    # now generate typeshed files for all scripts
    log.info("Generate type hint files (pyi) in folder: {}".format(STUB_FOLDER))
    utils.make_stub_files(STUB_FOLDER, levels=7)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(name)-10s %(levelname)-8s:%(message)s')

    get_all()
