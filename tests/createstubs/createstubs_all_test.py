# type: ignore reportGeneralTypeIssues
import sys
from collections import namedtuple
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Generator, List

import pytest
from mock import MagicMock
from packaging.version import Version, parse
from pytest_mock import MockerFixture

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib

from shared import LOCATIONS, VARIANTS, import_variant

pytestmark = pytest.mark.micropython

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
@pytest.mark.skip(reason="not sure if this is needed")
def test_firmwarestubber_base_version_match_package(
    location: Any,
    variant: str,
    mock_micropython_path: Generator[str, None, None],
):
    # Q&D Location
    path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    pyproject = tomllib.loads(open(str(path)).read())
    pyproject_version = pyproject["tool"]["poetry"]["version"]

    createstubs = import_variant(location, variant)
    # base version should match the package
    assert parse(createstubs.__version__).base_version == parse(pyproject_version).base_version


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
def test_stubber_info_basic(
    location: Any, variant: str, mock_micropython_path: Generator[str, None, None]
):
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
from testcases import fwid_test_cases


# @pytest.mark.parametrize("variant", VARIANTS)
# @pytest.mark.parametrize("location", LOCATIONS)
@pytest.mark.parametrize(
    "fwid,  sys_imp_name, sys_imp_version, sys_platform, os_uname, mock_modules",
    fwid_test_cases,
    ids=[e[0] for e in fwid_test_cases],
)
@pytest.mark.mocked
def test_stubber_fwid(
    mock_micropython_path: Generator[str, None, None],
    # location: str,
    # variant: str,
    mocker: MockerFixture,
    fwid: str,
    sys_imp_name: str,
    sys_imp_version: tuple,
    sys_platform: str,
    os_uname: Dict,
    mock_modules: List[str],
):
    variant = "createstubs"
    location = "board"
    createstubs = import_variant(location, variant)

    # FIX-ME : This does not yet cover minified
    mod_name = f"stubber.board.{variant}"
    # class.property : just pass a value
    mocker.patch(f"{mod_name}.sys.platform", sys_platform)
    mocker.patch(f"{mod_name}.sys.implementation.name", sys_imp_name)
    mocker.patch(f"{mod_name}.sys.implementation.version", sys_imp_version)
    # class.method--> mock using function
    fake_uname = os_uname

    def mock_uname():
        return fake_uname

    mocker.patch(f"{mod_name}.os.uname", mock_uname, create=True)
    for mod in mock_modules:
        # mock that these modules can be imported without errors
        sys.modules[mod] = MagicMock()

    # now run the tests
    stubber = createstubs.Stubber()
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
    assert info["board"] != "", "stubber.info() - No board detected"

    new_fwid = stubber._fwid
    assert new_fwid != "none"

    chars = " .()/\\:$"
    for c in chars:
        assert c not in stubber.flat_fwid, "flat_fwid must not contain '{}'".format(c)

    # Does the firmware id match (at least the beginning)
    assert new_fwid.startswith(fwid), "fwid does not match"

    assert new_fwid == fwid, f"fwid: {new_fwid} does not match"


# # throws an error on the commandline
# @pytest.mark.skip(reason="test not working")
# @pytest.mark.parametrize("variant", VARIANTS)
# @pytest.mark.parametrize("location", LOCATIONS)
# def test_read_path(
#     location,
#     variant,
#     mock_micropython_path,
# ):
#     # import createstubs  # type: ignore
#     createstubs = import_module(f"{location}.{variant}")  # type: ignore

#     assert createstubs.read_path() == ""


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

    stublist = list(tmp_path.glob("**/*.py"))
    assert len(stublist) == 3
    stubber.report()
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
    # just in the test folder , no structure
    stubber.create_module_stub("json", str(tmp_path / "json.py"))
    stubber.create_module_stub("_thread", str(tmp_path / "_thread.py"))

    stublist = list(tmp_path.glob("**/*.py"))
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

    stubber.create_module_stub("json")
    stublist = list((tmp_path / "stubs" / myid.lower()).glob("**/*.py"))
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
    # just in the test folder , no structure
    stubber.create_module_stub("urllib/request", str(tmp_path / "request.py"))
    stublist = list(tmp_path.glob("**/*.py"))
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
    # this should not generate a module , but also should not th
    stubber.create_module_stub("notamodule1", str(tmp_path / "notamodule1.py"))
    stubber.create_module_stub("not/amodule2", str(tmp_path / "notamodule2.py"))
    stublist = list(tmp_path.glob("**/*.py"))
    assert len(stublist) == 0


# def test_clean(tmp_path):
# import createstubs  # type: ignore
#    createstubs = import_module(f"{location}.{variant}")  # type: ignore
#     myid = "MyCustomID"
#     test_path = str(tmp_path)
#     stub_path =  Path(test_path) /"stubs"/ myid.lower()
#     stubber = Stubber(path = test_path, firmware_id=myid)
#     stubber.clean()

#     #Create a file
#     stubber.create_module_stub("json", PurePosixPath( stub_path / "json.py") )
#     stublist = list(Path(test_path).glob('**/*.py'))
#     assert len(stublist) == 1
#     stubber.clean()
