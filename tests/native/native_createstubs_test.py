# run createstubs in the unix version of micropython
import json
import os
import subprocess
import sys
from pathlib import Path

import distro
import pytest
from _pytest.config import Config

# "list of avaialble micropython versions on the current platfor"
fw_list = []  # no tests on mac
# Figure out ubuntu version
os_distro_version = f"{sys.platform}-{distro.id()}-{distro.version()}"

if os_distro_version in ["linux-ubuntu-20.04", "linux-debian-11"]:
    # Default = 20.04 - focal
    fw_list = [
        "ubuntu_20_04/micropython_v1_11",
        "ubuntu_20_04/micropython_v1_12",
        "ubuntu_20_04/micropython_v1_14",
        "ubuntu_20_04/micropython_v1_15",
        "ubuntu_20_04/micropython_v1_16",
        "ubuntu_20_04/micropython_v1_17",
        "ubuntu_20_04/micropython_v1_18",
    ]
elif os_distro_version in ["linux-ubuntu-18.04"]:
    # 18.04 - bionic
    fw_list = [
        "ubuntu_18_04/micropython_1_12",
        "ubuntu_18_04/micropython_1_13",
        "ubuntu_18_04/pycopy_3_3_2-25",
    ]
# distro does not cover windows... but no problem as long as it is not 16 bit it will run.
elif sys.platform == "win32":
    fw_list = [
        "windows/micropython_v1_18.exe",
    ]


# specify the minified tests using a marker
@pytest.mark.parametrize(
    "suffix",
    [
        pytest.param(""),
        pytest.param("_min", marks=pytest.mark.minified),
        # pytest.param("_mpy", marks=pytest.mark.minified), # TODO: add mpy tests including compiling to the correct version
    ],
)
@pytest.mark.parametrize(
    "variant",
    [
        pytest.param("createstubs"),
        pytest.param("createstubs_mem"),
        pytest.param("createstubs_db"),
    ],
)
@pytest.mark.parametrize(
    "firmware",
    fw_list,
)
def test_createstubs(firmware: str, variant: str, suffix: str, tmp_path: Path, pytestconfig: Config):
    "run createstubs in the native (linux/windows) version of micropython"

    # skip this on windows - python 3.7
    # TODO: why does it not work?
    if sys.platform == "win32":  # and sys.version_info[0] == 3 and sys.version_info[0] == 7:
        pytest.skip(msg="Test does not work well on Windows ....")

    # all createstub variants are in the same folder
    script_path = (pytestconfig.rootpath / "src" / "stubber" / "board").absolute()
    script_name = variant + suffix + ".py"
    # other tests may / will change the CWD to a different folder
    fw_filename = (pytestconfig.rootpath / "tests" / "tools" / firmware).absolute()  # .as_posix()
    cmd = [fw_filename.as_posix(), script_name, "--path", str(tmp_path)]

    # check if the script exists
    assert (script_path / script_name).exists(), f"script {script_name} does not exist"
    # Delete database before the test
    if variant == "createstubs_db":
        if firmware.endswith("v1_11"):
            pytest.skip(reason="v1.11 has no machine module")  # type: ignore
        (script_path / "modulelist.db").unlink(missing_ok=True)
        (script_path / "modulelist.done").unlink(missing_ok=True)

    print(" ".join(cmd))
    try:
        subproc = subprocess.run(
            cmd,
            cwd=script_path,
            timeout=100000,
            capture_output=False,
        )
        print(subproc.stdout)
        assert subproc.returncode == 0, "createstubs ran with an error :" + str(subproc.stdout)
        # assert (subproc.returncode <= 0 ), "createstubs ran with an error"
    except ImportError as e:
        print(e)
        pass
    except BaseException as e:
        print(e)
        pass

    # did it run without error ?

    stub_path = tmp_path / "stubs"
    stubfiles = list(stub_path.rglob("*.py"))

    # manifest exists
    jsons = list(stub_path.rglob("modules.json"))
    assert len(jsons) == 1, "there should be 1 manifest"

    # manifest is valid json
    # read file
    manifest = None
    with open(jsons[0], "r") as file:
        manifest = json.load(file)

    for x in ["firmware", "stubber", "modules"]:
        assert x in manifest.keys(), "module manifest should contain firmware, stubber , modules"

    assert len(manifest["modules"]) - len(stubfiles) == 0, "number of modules must match count of stubfiles."
    # Delete databaseafter the test
    if variant == "createstubs_db":
        (script_path / "modulelist.done").unlink(missing_ok=False)  # MUST exist
        (script_path / "modulelist.db").unlink(missing_ok=True)  # may not exist

    assert len(stubfiles) >= 25, "There should be 25 stubs or more"
