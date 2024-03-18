# type: ignore reportGeneralTypeIssues
import os
import sys
from collections import namedtuple
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Generator, List, NamedTuple, Optional

import pytest
from mock import MagicMock
from packaging.version import Version, parse
from pytest_mock import MockerFixture

pytestmark = [pytest.mark.stubber]

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib

from shared import LOCATIONS, VARIANTS, import_variant

pytestmark = [pytest.mark.stubber, pytest.mark.micropython]

UName = namedtuple("UName", ["sysname", "nodename", "release", "version", "machine"])

FIRST_VERSION = None


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_firmwarestubber_all_versions_same(
    location: Any,
    variant: str,
    mock_micropython_path: Generator[str, None, None],
):
    global FIRST_VERSION

    createstubs = import_variant(location, variant)

    if not FIRST_VERSION:
        FIRST_VERSION = parse(createstubs.__version__)
    # all versions should be the same
    assert FIRST_VERSION == parse(createstubs.__version__)


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_stubber_Class_available(
    location: Any,
    variant: str,
    mock_micropython_path: Generator[str, None, None],
):
    createstubs = import_variant(location, variant)

    assert createstubs.Stubber is not None, "Stubber Class not imported"


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_stubber_info_basic(location: Any, variant: str, mock_micropython_path: Generator[str, None, None]):
    createstubs = import_variant(location, variant)
    stubber = createstubs.Stubber()
    assert stubber is not None, "Can't create Stubber instance"

    info = createstubs._info()
    print(info)
    assert info["family"] != "", "stubber.info() - No Family detected"
    assert info["port"] != "", "stubber.info() - No port detected"
    assert info["ver"] != "", "stubber.info() - No clean version detected"

    assert stubber._fwid != "none"

    assert " " not in stubber.flat_fwid, "flat_fwid must not contain any spaces"
    assert "." not in stubber.flat_fwid, "flat_fwid must not contain any dots"


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_stubber_info_custom(
    location: Any,
    variant: str,
    fx_add_minified_path: Generator[str, None, None],
    mock_micropython_path: Generator[str, None, None],
):
    createstubs = import_variant(location, variant)

    myid = "MyCustomID"
    stubber = createstubs.Stubber(firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"

    assert stubber._fwid != "none"
    assert stubber._fwid == myid.lower()


#################################################
# test the fwid naming on the different platforms
#################################################
from testcases import MP_Implementation, fwid_test_cases


# @pytest.mark.parametrize("variant", VARIANTS)
# @pytest.mark.parametrize("location", LOCATIONS)
@pytest.mark.parametrize(
    "fwid,  sys_implementation, sys_platform, sys_version, os_uname, mock_modules",
    fwid_test_cases,
    ids=[e[0] for e in fwid_test_cases],
)
@pytest.mark.mocked
def test_stubber_fwid(
    mock_micropython_path: Generator[str, None, None],
    mocker: MockerFixture,
    fwid: str,
    sys_implementation: MP_Implementation,
    sys_platform: str,
    sys_version: str,
    os_uname: Dict,
    mock_modules: List[str],
):
    variant = "createstubs"
    location = "board"
    createstubs = import_variant(location, variant)

    mod_name = f"stubber.board.{variant}"
    # class.property : just pass a value
    mocker.patch(f"{mod_name}.sys.platform", sys_platform)
    # fatch sys.implementation
    mocker.patch(f"{mod_name}.sys.implementation.name", sys_implementation.name)
    mocker.patch(f"{mod_name}.sys.implementation.version", sys_implementation.version)
    mocker.patch(f"{mod_name}.sys.version", sys_version)
    if sys_implementation._machine:
        mocker.patch(f"{mod_name}.sys.implementation._machine", sys_implementation._machine, create=True)
    if sys_implementation._mpy:
        mocker.patch(f"{mod_name}.sys.implementation._mpy", sys_implementation._mpy, create=True)
    # class.method--> mock using function

    if os_uname:
        # only mock uname if there is something to mock
        fake_uname = os_uname

        def mock_uname():
            return fake_uname

        mocker.patch(f"{mod_name}.os.uname", mock_uname, create=True)

    for mod in mock_modules:
        # mock that these modules can be imported without errors
        sys.modules[mod] = MagicMock()

    # change to the folder with the data files for the test
    old_cwd = os.getcwd()
    os.chdir("./src/stubber/data")
    try:
        # now run the tests
        stubber = createstubs.Stubber()
    finally:
        # change back to the original folder
        os.chdir(old_cwd)
    assert stubber is not None, "Can't create Stubber instance"
    info = createstubs._info()

    for mod in mock_modules:
        # unmock the module
        del sys.modules[mod]

    # print("\nvalidating: " + fwid)
    # print(info)

    assert info["family"] != "", "stubber.info() - No Family detected"
    assert info["version"] != "", "stubber.info() - No clean version detected"
    assert Version(info["version"]), "provided version is not a valid version"

    assert info["port"] != "", "stubber.info() - No port detected"
    # TEST 2: check if the firmware id is correct
    new_fwid = stubber._fwid
    assert new_fwid != "none"

    chars = " .()/\\:$"
    for c in chars:
        assert c not in stubber.flat_fwid, "flat_fwid must not contain '{}'".format(c)

    # Does the firmware id match (at least the part before the last -)

    short_fwid = "-".join(fwid.split("-", 2)[:2])
    assert new_fwid.startswith(short_fwid), f"fwid: {new_fwid} does not start with {short_fwid}"

    if not "esp8266" in fwid:
        # TODO: Fix FWID logic with esp8266
        assert new_fwid == fwid, f"fwid: {new_fwid} does not match"


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_create_all_stubs(
    location: Any,
    variant: str,
    tmp_path: Path,
    mock_micropython_path: Generator[str, None, None],
):
    createstubs = import_variant(location, variant)

    myid = "MyCustomID"

    stubber = createstubs.Stubber(path=str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    stubber.modules = ["json", "_thread", "array"]
    stubber.add_modules(["http_client", "webrepl", "_internal"])
    stubber.create_all_stubs()

    stublist = list(tmp_path.glob("**/*.pyi"))
    assert len(stublist) == 3
    stublist = list(tmp_path.glob("**/modules.json"))
    assert len(stublist) == 1

    stubber.clean()
    stublist = list(tmp_path.glob("**/*.*"))
    assert len(stublist) == 0


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_get_root(
    location: Any,
    variant: str,
    mock_micropython_path: Generator[str, None, None],
):
    createstubs = import_variant(location, variant)

    x = createstubs.get_root()
    assert type(x) == str
    assert len(x) > 0


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_create_module_stub(
    location: Any,
    variant: str,
    tmp_path: Path,
    mock_micropython_path: Generator[str, None, None],
):
    createstubs = import_variant(location, variant)

    myid = "MyCustomID"
    stubber = createstubs.Stubber(path=str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    stubber.report_start()
    # just in the test folder , no structure
    stubber.create_module_stub("json", str(tmp_path / "json.pyi"))
    stubber.create_module_stub("_thread", str(tmp_path / "_thread.pyi"))

    stublist = list(tmp_path.glob("**/*.pyi"))
    assert len(stublist) == 2


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_create_module_stub_folder(
    location: Any,
    variant: str,
    mock_micropython_path: Generator[str, None, None],
    tmp_path: Path,
):
    createstubs = import_variant(location, variant)

    myid = "MyCustomID"
    stubber = createstubs.Stubber(path=str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    stubber.report_start()
    stubber.create_module_stub("json")
    stublist = list((tmp_path / "stubs" / myid.lower()).glob("**/*.pyi"))
    assert len(stublist) == 1, "should create stub in stub folder if no folder specified"


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_create_module_stub_ignored(
    location: Any,
    variant: str,
    mock_micropython_path: Generator[str, None, None],
    tmp_path: Path,
):
    createstubs = import_variant(location, variant)

    myid = "MyCustomID"
    stubber = createstubs.Stubber(path=str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    # should not generate
    stubber.create_one_stub("upysh")
    stubber.create_one_stub("http_client")
    stubber.create_one_stub("webrepl")

    stublist = list(tmp_path.glob("**/*.py"))
    assert len(stublist) == 0


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_nested_modules(
    location: Any,
    variant: str,
    mock_micropython_path: Generator[str, None, None],
    tmp_path: Path,
):
    createstubs = import_variant(location, variant)

    myid = "MyCustomID"
    stubber = createstubs.Stubber(path=str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    stubber.report_start()
    # just in the test folder , no structure
    stubber.create_module_stub("urllib/request", str(tmp_path / "request.pyi"))
    stublist = list(tmp_path.glob("**/*.pyi"))
    assert len(stublist) == 1


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_unavailable_modules(
    location: Any,
    variant: str,
    mock_micropython_path: Generator[str, None, None],
    tmp_path: Path,
):
    createstubs = import_variant(location, variant)

    myid = "MyCustomID"
    stubber = createstubs.Stubber(path=str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    stubber.report_start()
    # this should not generate a module , but also should not th
    stubber.create_module_stub("notamodule1", str(tmp_path / "notamodule1.pyi"))
    stubber.create_module_stub("not/amodule2", str(tmp_path / "notamodule2.pyi"))
    stublist = list(tmp_path.glob("**/*.pyi"))
    assert len(stublist) == 0


@pytest.mark.parametrize(
    "input, expected",
    [
        ("", ""),
        ("v1.13 on 2020-10-09", ""),
        ("v1.13-103-gb137d064e on 2020-10-09", "103"),
        ("3.4.0; MicroPython v1.23.0-preview.6.g3d0b6276f on 2024-01-02", "6"),
        ("3.4.0; MicroPython v1.22.0 on 2023-12-27", ""),
    ],
)
def test_build(input: str, expected: str):
    """build function should be able to extract from
    - sys.version
    - sys.implementation.version
    """
    variant = "createstubs"
    location = "board"
    createstubs = import_variant(location, variant)

    outcome = createstubs._build(input)
    assert outcome == expected
