import os
import glob
import json
import logging
from version import VERSION
from pathlib import Path

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


def cleanup(modules_folder:Path):
    " Q&D cleanup "
    # for some reason the umqtt simple.pyi and robust.pyi are created twice 
    #  - modules_root folder ( simple.pyi and robust.pyi) - NOT OK 
    #       - umqtt folder (simple.py & pyi and robust.py & pyi) OK
    #  similar for mpy 1.9x - 1.11
    #       - core.pyi          - uasyncio\core.py'
    #       - urequests.pyi     - urllib\urequest.py'
    # Mpy 1.13+
    #       - uasyncio.pyi      -uasyncio\__init__.py


    #todo - Add check for source folder 
    for file_name in 'simple.pyi','robust.pyi','core.pyi','urequest.pyi','uasyncio.pyi':
        f = Path.joinpath(modules_folder, file_name)
        if f.exists():
            try:
                print(' - removing {}'.format(f))
                f.unlink()
            except OSError:
                log.error(' * Unable to remove extranous stub {}'.format(f) )
                pass



def make_stub_files(stub_path:str, levels: int = 0):
    "generate typeshed files for all scripts in a folder using mypy/stubgen"
    # levels is ignored for backward compat with make_stub_files_old
    # stubgen cannot process folders with duplicate modules ( ie v1.14 and v1.15 )

    modlist = list(Path(stub_path).glob('**/modules.json'))
    for file in modlist:
        modules_folder = file.parent
        # clean before to clean any old stuff
        cleanup(modules_folder)

        print("running stubgen on {0}".format(modules_folder))
        cmd = "stubgen {0} --output {0} --include-private --ignore-errors".format(modules_folder)
        result = os.system(cmd)
        # Check on error
        if result != 0:
            # in clase of falure then Plan B 
            print('Failure on folder, attempt to stub per file.py')
            py_files = modules_folder.glob('**/*.py')
            for py in py_files:
                cmd = "stubgen {0} --output {1} --include-private --ignore-errors".format(py, py.parent)
                print(" >stubgen on {0}".format(py))
                result = os.system(cmd)

        # TODO: if general failure try to run stubgen on each *.py 

        # and clean after to only checkin good stuff
        cleanup(modules_folder)



def make_stub_files_old(stub_path, levels: int = 1):
    "generate typeshed files for all scripts in a folder using make_sub_files.py"
    level = ""
    # make_sub_files.py only does one folder level at a time
    # so lets try 7 levels /** ,  /**/** , etc
    # and does not work well if loaded as a module
    for i in range(levels):
        cmd = "python ./src/make_stub_files.py -c ./src/make_stub_files.cfg -u {}{}/*.py".format(stub_path, level)
        log.debug("level {} : {}".format(i+1, cmd))
        os.system(cmd)
        level = level + '/**'

def manifest(family=None, machine=None, port=None, platform=None, sysname=None, nodename=None, version=None, release=None, firmware=None) -> dict:
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
    try:
        for filename in glob.glob(os.path.join(folder, "*.py")):
            f_name, _ = os.path.splitext(os.path.basename(filename))
            mod_manifest['modules'].append({ "file": os.path.basename(filename), "module":f_name})
        #write the the module manifest
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

