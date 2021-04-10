#!/usr/bin/env python3
"""
Collect modules and python stubs from other projects and stores them in the all_stubs folder
The all_stubs folder should be mapped/symlinked to the micropython_stubs/stubs repo/folder

"""
# pylint: disable= line-too-long, W1202
# Copyright (c) 2020 Jos Verlinde
# MIT license
# pylint: disable= line-too-long
import logging
import utils

log = logging.getLogger(__name__)

if __name__ == "__main__":
    # now generate typeshed files for all scripts
    log.info("Generate type hint files (pyi) in folder: {}".format(utils.STUB_FOLDER))
    utils.make_stub_files(utils.STUB_FOLDER, levels=7)