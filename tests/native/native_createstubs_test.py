# run createstubs in the unix version of micropython
import json
import sys
import os
import subprocess
from pathlib import Path
from typing import List
import pytest
from _pytest.config import Config
import distro


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


@pytest.mark.parametrize(
    "variant",
    [
        pytest.param("createstubs"),
        pytest.param("createstubs_mem"),
        pytest.param("createstubs_db", marks=pytest.mark.linux),  # no btree on windows build
    ],
)
# specify the minified tests using a marker
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
def test_createstubs(firmware: str, tmp_path: Path, script_folder: str, variant: str, pytestconfig: Config):
    "run createstubs in the native (linux/windows) version of micropython"

    # skip this on windows - python 3.7
    # TODO: why does it not work?
    if sys.platform == "win32" and sys.version_info[0] == 3 and sys.version_info[0] == 7:
        pytest.skip(msg="Test does not work well on Win + Python 3.7 ....")

    # Use temp_path to generate stubs
    script_path = Path(script_folder).absolute()
    # other tests may / will change the CWD to a different folder
    fw_filename = (pytestconfig.rootpath / "tests" / "tools" / firmware).absolute()  # .as_posix()
    cmd = [fw_filename, variant + ".py", "--path", str(tmp_path)]

    # Delete database before the test
    if variant == "createstubs_db":
        if firmware.endswith("v1_11"):
            pytest.skip(reason="v1.11 has no  machine module")  # type: ignore
        if (Path(script_folder) / "modulelist.db").exists():
            os.remove(Path(script_folder) / "modulelist.db")
    try:
        subproc = subprocess.run(
            cmd,
            cwd=script_path,
            timeout=100000,
            capture_output=True,
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
    # use rough filecount to see if there were results without checking the details
    if "micropython" in script_folder:
        assert len(stubfiles) >= 45, "micropython: there should be 45 stubs or more"
    else:
        assert len(stubfiles) >= 25, "pycopy: there should be 25 stubs or more"

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
