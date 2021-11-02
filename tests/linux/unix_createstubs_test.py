# run createstubs in the unix version of micropython
import os
import json
import sys
import subprocess
from pathlib import Path
from typing import List
import pytest

#  ROOT = Path(__file__).parent

import platform


@pytest.fixture(scope="module")
def ubuntu_ver_sion():
    "find the version of ubuntu we are running on"
    version = ""
    for v in ("18.04", "20.04"):
        if v in platform.version() and "Ubuntu" in platform.version():
            version = v
    if version != "":
        folder = f"ubuntu_{version}".replace(".", "_")
        return folder
        print("ubuntu :", version)
    return ""


def firmwares() -> List[str]:
    if "18.04" in platform.version() and "Ubuntu" in platform.version():
        return [
            "micropython_1_12",
            "micropython_1_13",
            "pycopy_3_3_2-25",
        ]
    if "20.04" in platform.version() and "Ubuntu" in platform.version():
        return [
            "micropython_v1_11",
            "micropython_v1_12",
            "micropython_v1_14",
            "micropython_v1_15",
            "micropython_v1_16",
        ]
    return []


@pytest.mark.parametrize("script_folder", ["./board", "./minified"])
@pytest.mark.parametrize("firmware", firmwares())

# only run createsubs in the unix version of micropython
@pytest.mark.skipif(sys.platform == "win32", reason="requires linux")
def test_createstubs(firmware, tmp_path, script_folder, ubuntu_ver_sion):
    # Use temp_path to generate stubs
    scriptfolder = os.path.abspath(script_folder)
    cmd = [
        os.path.abspath("tests/tools/" + ubuntu_ver_sion + "/" + firmware),
        "createstubs.py",
        "--path",
        tmp_path,
    ]
    try:
        subproc = subprocess.run(cmd, cwd=scriptfolder, timeout=100000)
        assert subproc.returncode == 0, "createstubs ran with an error"
        # assert (subproc.returncode <= 0 ), "createstubs ran with an error"
    except ImportError as e:
        print(e)
        pass
    # did it run without error ?

    stubfolder = Path(tmp_path) / "stubs"
    stubfiles = list(stubfolder.rglob("*.py"))
    # filecount
    if "micropython" in script_folder:
        assert len(stubfiles) >= 45, "micropython: there should be 45 stubs or more"
    else:
        assert len(stubfiles) >= 30, "pycopy: there should be 30 stubs or more"

    # manifest exists
    jsons = list(stubfolder.rglob("modules.json"))
    assert len(jsons) == 1, "there should be 1 manifest"

    # manifest is valid json
    # read file
    manifest = None
    with open(jsons[0], "r") as file:
        manifest = json.load(file)

    assert len(manifest) == 3, "module manifest should contain firmware, stubber , modules"

    assert len(manifest["modules"]) == len(stubfiles), "number of modules must match count of stubfiles"
