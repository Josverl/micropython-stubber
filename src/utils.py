import os
import glob
import json
import logging
from version import VERSION

log = logging.getLogger(__name__)

STUB_FOLDER = './all-stubs'

def clean_version(version: str, build: bool = False):
    "omit the commit hash from the git tag"
    # 'v1.13-103-gb137d064e' --> 'v1.13-103'
    nibbles = version.split('-')
    if len(nibbles) == 1:
        return version
    elif build and build != 'dirty':
        return '-'.join(version.split('-')[0:-1])
    else:
        return '-'.join((version.split('-')[0], 'N'))

def stubfolder(path: str)->str:
    "return path in the stub folder"
    return '{}/{}'.format(STUB_FOLDER, path)

def flat_version(version: str):
    "Turn version from 'v1.2.3' into '1_2_3' to be used in filename"
    return version.replace('v', '').replace('.', '_')

def make_stub_files(stub_path, levels: int = 1):
    "generate typeshed files for all scripts in a folder"
    level = ""
    # make_sub_files.py only does one folder level at a time
    # so lets try 7 levels /** ,  /**/** , etc
    # and does not work well if loaded as a module
    for i in range(levels):
        cmd = "python ./src/make_stub_files.py -c ./src/make_stub_files.cfg -u {}{}/*.py".format(stub_path, level)
        log.debug("level {} : {}".format(i+1, cmd))
        os.system(cmd)
        level = level + '/**'

def manifest(family:str=None, machine:str=None, port:str=None, platform:str=None, sysname:str=None, nodename:str=None, version:str=None, release:str=None, firmware:str=None) -> dict:
    "create a new empty manifest dict"
    if  family is None:
        family = 'micropython' #family
    if  machine is None:
        machine = family       #family

    if  port is None:
        port = 'common'       #family
    if  platform is None:
        platform = port       #family

    if  version is None:
        version = '0.0.0'

    if  nodename is None:
        nodename = sysname
    if  release is None:
        release = version
    if  firmware is None:
        firmware = "{}-{}-{}".format(family, port, flat_version(version))

    mod_manifest = {"firmware": {
                        "family": family,
                        "port": port,
                        "platform": platform,
                        "machine": machine,
                        "firmware": firmware,
                        "nodename": nodename,
                        "version": version,
                        "release": release,
                        "sysname": sysname
                    },
                    "stubber": {
                        "version": VERSION
                    },
                    "modules": []
                }
    return mod_manifest

def make_manifest(folder: str, family: str, port: str, version: str)-> bool:
    mod_manifest = manifest(family=family, port=port, sysname=family, version=version)
    mods = []
    try:
        for filename in glob.glob(os.path.join(folder, "*.py")):
            f_name, _ = os.path.splitext(os.path.basename(filename))
            mods.append({ "file": os.path.basename(filename), "module":f_name})
        if len(mods) == 0:
            return False
        # sort the list of module manifests on filename
        mod_manifest['modules'] =  sorted(mods, key=lambda m: m['file'])
        # write the the module manifest
        with open(os.path.join(folder, "modules.json"), "w") as outfile:
            json.dump(mod_manifest, outfile)
        return True
    except OSError:
        return False

def generate_all_stubs():
    "just create typeshed stubs"
    # now generate typeshed files for all scripts
    print("Generate type hint files (pyi) in folder: {}".format(STUB_FOLDER))
    make_stub_files(STUB_FOLDER, levels=7)

