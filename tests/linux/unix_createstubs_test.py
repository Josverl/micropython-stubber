# run createstubs in the unix version of micropython
from logging import captureWarnings
import os
import json
import sys
import subprocess
from pathlib import Path
from typing import List
import pytest
import distro


ubuntu_version = "?"
fw_list = []
# Figure out ubuntu version
if sys.platform == "linux":
    if distro.id() == "ubuntu":
        ubuntu_version = distro.version()


# Default = 20.04 - focal
fw_list = [
    "ubuntu_20_04/micropython_v1_11",
    "ubuntu_20_04/micropython_v1_12",
    "ubuntu_20_04/micropython_v1_14",
    "ubuntu_20_04/micropython_v1_15",
    "ubuntu_20_04/micropython_v1_16",
]
if ubuntu_version == "18.04":
    # 18.04 - bionic
    fw_list = [
        "ubuntu_18_04/micropython_1_12",
        "ubuntu_18_04/micropython_1_13",
        "ubuntu_18_04/pycopy_3_3_2-25",
    ]

# more cmplex config to specify the minified tests
@pytest.mark.parametrize(
    "script_folder",
    [
        pytest.param("./board"),
        pytest.param("./minified", marks=pytest.mark.minified),
    ],
)
@pytest.mark.parametrize(
    "firmware",
    fw_list,
)
# only run createsubs in the unix version of micropython
@pytest.mark.linux
def test_createstubs(firmware, tmp_path: Path, script_folder):
    # Use temp_path to generate stubs
    scriptfolder = os.path.abspath(script_folder)
    cmd = [os.path.abspath("tests/tools/ubuntu_20_04/" + firmware), "createstubs.py", "--path", str(tmp_path)]

    try:
        subproc = subprocess.run(
            cmd,
            cwd=scriptfolder,
            timeout=100000,
            capture_output=True,
        )
        print(subproc.stdout)
        assert subproc.returncode == 0, "createstubs ran with an error :" + str(subproc.stdout)
        # assert (subproc.returncode <= 0 ), "createstubs ran with an error"
    except ImportError as e:
        print(e)
        pass
    # did it run without error ?

    stubfolder = tmp_path / "stubs"
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

    assert len(manifest["modules"]) - len(stubfiles) == 0, "number of modules must match count of stubfiles."
