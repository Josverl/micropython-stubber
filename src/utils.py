import os
import json
import logging
log = logging.getLogger(__name__)

STUB_FOLDER = './all-stubs'

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

def stubfolder(path:str)->str:
    "return path in the stub folder"
    return '{}/{}'.format(STUB_FOLDER,path)

def flat_version(version: str):
    "Turn version from 'v1.2.3' into '1_2_3' to be used in filename"
    return version.replace('v', '').replace('.', '_')

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

def manifest(machine:None,sysname=None,nodename=None,version=None,release=None,firmware=None) -> dict:
    "create a new empty manifest dict"
    if  machine is None:
        machine = 'micropython' #family
    if  sysname is None:
        sysname = 'mpy'         # short
    if  nodename is None:
        nodename = sysname
    if  version is None:
        version = '0.0.0'
    if  release is None:
        release = version
    if  firmware is None:
        firmware = sysname + ' ' + version

    mod_manifest ={ "firmware": {
                        "machine": machine,
                        "firmware": firmware,
                        "nodename": nodename,
                        "version": version,
                        "release": release,
                        "sysname": sysname
                    },
                    "stubber": {
                        "version": version
                    },
                    "modules": []
                }
    return mod_manifest

