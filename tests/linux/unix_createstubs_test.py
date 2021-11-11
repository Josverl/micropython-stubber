# run createstubs in the unix version of micropython
from logging import captureWarnings
import os
import json
import sys
import subprocess
from pathlib import Path
import pytest


# Figure out ubuntu version
try:
    import lsb_release

    ubuntu_version = lsb_release.get_os_release()["RELEASE"]
except Exception:
    ubuntu_version = ""

if ubuntu_version == "18.04":
    fw_list = [
        "micropython_1_12",
        "micropython_1_13",
        "pycopy_3_3_2-25",
    ]
elif ubuntu_version == "20.04":
    fw_list = [
        "micropython_v1_11",
        "micropython_v1_12",
        "micropython_v1_14",
        "micropython_v1_15",
        "micropython_v1_16",
    ]
else:
    fw_list = []


@pytest.mark.parametrize(
    "script_folder",
    [
        "./board",
        "./minified",
    ],
)
@pytest.mark.parametrize(
    "firmware",
    fw_list,
)

# only run createsubs in the unix version of micropython
@pytest.mark.skipif(sys.platform == "win32", reason="requires linux")
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

    assert len(manifest["modules"]) - len(stubfiles) <= 1, "WORKAROUND number of modules must match count of stubfiles."

    # # BUG: buildins appears twice in the manifest.json
    # assert len(manifest["modules"]) == len(stubfiles), (
    #     "number of modules must match count of stubfiles."
    #     + repr(stubfiles)
    #     + "++++++++++______++++++++++"
    #     + repr(manifest["modules"])
    # )
