"""
Download or update the micropyton compatibility modules from pycopy and stores them in the all_stubs folder
The all_stubs folder should be mapped/symlinked to the micropython_stubs/stubs repo/folder
"""

import os
import shutil
import subprocess
import logging
import json

import utils
from pathlib import Path
from version import __version__

log = logging.getLogger(__name__)


def get_core(requirements, stub_path=None, family: str = "core"):
    "Download MicroPython compatibility modules"
    if not stub_path:
        stub_path = "./all-stubs/cpython-core"
    stub_path = Path(stub_path)

    # use pip to dowload requirements file to build folder in one go
    #   pip install --no-compile --no-cache-dir --target ./scratch/test --upgrade -r ./src/micropython.txt
    build_path = Path("./build").absolute()
    os.makedirs(stub_path, exist_ok=True)
    os.makedirs(build_path, exist_ok=True)
    mod_manifest = None
    modlist = []
    try:
        subprocess.run(
            [
                "pip",
                "install",
                "--target",
                build_path.as_posix(),
                "-r",
                requirements,
                "--no-cache-dir",
                "--no-compile",
                "--upgrade",
                "--no-binary=:all:",
            ],
            capture_output=False,
            check=True,
        )

    except OSError as err:
        log.error("An error occurred while trying to run pip to download the MicroPython compatibility modules from PyPi: {}".format(err))

    # copy *.py files in build folder to stub_path
    # sort by filename to reduce churn in the repo
    for filename in sorted(build_path.rglob("*.py")):
        log.info("pipped : {}".format(filename.name))
        # f_name, f_ext = os.path.splitext(os.path.basename(filename))  # pylint: disable=unused-variable
        modlist.append({"file": filename.name, "module": filename.stem})
        try:
            shutil.copy2(filename, stub_path)
        except OSError as err:
            log.exception(err)
    # remove build folder
    shutil.rmtree(build_path, ignore_errors=True)
    # build modules.json
    mod_manifest = utils.manifest(family="cpython-core", port=family, version=__version__, stubtype="core", platform="cpython")
    mod_manifest["modules"] += modlist

    if mod_manifest and len(modlist):
        # write the the module manifest for the cpython core modules
        with open(stub_path / "modules.json", "w") as outfile:
            json.dump(mod_manifest, outfile, indent=4, sort_keys=True)


if __name__ == "__main__":
    # just run a quick test
    logging.basicConfig(format="%(levelname)-8s:%(message)s", level=logging.INFO)
    get_core(requirements="./requirements-core-pycopy.txt", stub_path="./scratch/cpython_common")
