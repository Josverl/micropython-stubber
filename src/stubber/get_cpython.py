"""
Download or update the micropyton compatibility modules from pycopy and stores them in the all_stubs folder
The all_stubs folder should be mapped/symlinked to the micropython_stubs/stubs repo/folder
"""
# pragma: no cover
import json
import os
import pkgutil
import shutil
import subprocess
import tempfile
from pathlib import Path

from loguru import logger as log

from . import __version__, utils
from .utils.config import CONFIG

# # log = logging.getLogger(__name__)


def get_core(requirements, stub_path=None, family: str = "core"):
    "Download MicroPython compatibility modules"
    if not stub_path:
        stub_path = CONFIG.stub_path / "cpython-core"  # pragma: no cover
    stub_path = Path(stub_path)

    # use pip to dowload requirements file to build folder in one go
    #   pip install --no-compile --no-cache-dir --target ./scratch/test --upgrade -r ./src/micropython.txt

    os.makedirs(stub_path, exist_ok=True)
    # get a temp dir and clean up afterwards
    with tempfile.TemporaryDirectory() as tmpdir:
        build_path = Path(tmpdir).absolute()
        # os.makedirs(build_path, exist_ok=True)
        mod_manifest = None
        modlist = []

        # within package/mymodule1.py, for example

        data = pkgutil.get_data(__name__, "data/" + requirements)
        if not data:  # pragma: no cover
            raise Exception("Resource Not found")
        temp_file = tempfile.NamedTemporaryFile(prefix="requirements", suffix=".txt", delete=False)
        with temp_file.file as fp:
            fp.write(data)
            fp.close
        #
        req_filename = temp_file.name

        try:
            subprocess.run(
                [
                    "pip",
                    "install",
                    "--target",
                    build_path.as_posix(),
                    "-r",
                    req_filename,
                    "--no-cache-dir",
                    "--no-compile",
                    "--upgrade",
                    "--no-binary=:all:",
                ],
                capture_output=False,
                check=True,
            )

        except OSError as err:  # pragma: no cover
            log.error(
                "An error occurred while trying to run pip to download the MicroPython compatibility modules from PyPi: {}".format(err)
            )

        # copy *.py files in build folder to stub_path
        # sort by filename to reduce churn in the repo
        for filename in sorted(build_path.rglob("*.py")):
            log.debug("pipped : {}".format(filename.name))
            # f_name, f_ext = os.path.splitext(os.path.basename(filename))  # pylint: disable=unused-variable
            modlist.append({"file": filename.name, "module": filename.stem})
            try:
                shutil.copy2(filename, stub_path)
            except OSError as err:  # pragma: no cover
                log.exception(err)

    # build modules.json
    mod_manifest = utils.manifest(family="cpython-core", port=family, version=__version__, stubtype="core", platform="cpython")
    mod_manifest["modules"] += modlist

    if mod_manifest and len(modlist):
        # write the the module manifest for the cpython core modules
        with open(stub_path / "modules.json", "w") as outfile:
            json.dump(mod_manifest, outfile, indent=4, sort_keys=True)


if __name__ == "__main__":
    # just run a quick test
    # logging.basicConfig(format="%(levelname)-8s:%(message)s", level=logging.INFO)
    get_core(requirements="requirements-core-pycopy.txt", stub_path="./scratch/cpython_common")
