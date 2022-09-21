# others
import json
import subprocess
from pathlib import Path
from typing import Dict, List

import pytest
import stubber.basicgit as git

from helpers import read_stub

pytestmark = pytest.mark.doc_stubs

# SOT
from stubber.stubs_from_docs import TYPING_IMPORT, RSTReader, generate_from_rst

TEST_DOCFIX = False  # run the tests agains the doc_fix_branch
XFAIL_DOCFIX = True  # True to not fail on missing doc fixes


###################################################################################################
# Fixtures for re-use by different test methods
# shared across this module
###################################################################################################
@pytest.fixture(scope="module")
def pyright_results(rst_stubs):
    "Run pyright over folder with rst generated stubs, and return the results"
    # TODO: this fails if the nodeJS version of pyright is installed , and only works for the SLOWER pip install Pyright

    cmd = ["pyright", "--project", "tests/pyrightconfig.json", "--outputjson", rst_stubs.as_posix()]
    try:
        # run pyright in the docstub folder to allow modules to import each other.
        result = subprocess.run(cmd, shell=False, capture_output=True, cwd=rst_stubs.as_posix())
    except OSError as e:
        raise e
    results = {}
    try:
        results = json.loads(result.stdout)
    except Exception:
        assert 0, "Could not load pyright's JSON output :-("
    return results


@pytest.fixture(scope="module")
def micropython_repo(testrepo_micropython: Path, testrepo_micropython_lib: Path):
    "make sure a recent branch is checked out"

    git.switch_branch("master", testrepo_micropython.as_posix())
    if TEST_DOCFIX:
        # run test against the proposed documentation fixes
        try:
            git.switch_branch("fix_lib_documentation", testrepo_micropython.as_posix())
        except Exception:
            # git.switch_branch("master", MICROPYTHON_FOLDER)
            git.checkout_commit("micropython/master")

    v_tag = git.get_tag(testrepo_micropython.as_posix()) or "xx_x"
    yield v_tag


# TODO: Source version and tag
@pytest.fixture(scope="module")
def rst_stubs(tmp_path_factory: pytest.TempPathFactory, micropython_repo, testrepo_micropython: Path):
    "Generate stubs from RST files - once for this module"
    v_tag = micropython_repo
    # setup our on folder for testing
    dst_folder = tmp_path_factory.mktemp("stubs") / v_tag
    rst_folder = testrepo_micropython / "docs/library"
    generate_from_rst(rst_folder, dst_folder, v_tag=v_tag)
    yield dst_folder

    # cleanup code here


###################################################################################################
#
###################################################################################################


# # @pytest.mark.xfail(reason="upstream docfix needed", condition=XFAIL_DOCFIX)
@pytest.mark.docfix
def test_rst_all(tmp_path, micropython_repo, testrepo_micropython: Path):
    v_tag = micropython_repo

    rst_folder = Path(testrepo_micropython.as_posix()) / "docs/library"
    dst_folder = tmp_path / "noblack"
    x = generate_from_rst(rst_folder, dst_folder, v_tag=v_tag)
    assert type(x) == int, "returns a number"
    assert x > 0, "should generate at least 1 file"


EXP_10 = [
    "def wake_on_ext0(pin, level) -> Any:",
    "def wake_on_ext0(pin, level) -> Any:",
]


@pytest.mark.parametrize(
    "filename, expected",
    [
        (
            "tests/rst/data/function_10.rst",
            [
                "def wake_on_ext0(pin, level) -> Any:",
            ],
        ),
        (
            "tests/rst/data/function_11.rst",
            [
                "def wake_on_ext0(pin, level) -> Any:",
            ],
        ),
        (
            "tests/rst/data/function_12.rst",
            [
                "def wake_on_touch(wake) -> None:",
                "        Configure whether or not a touch will wake the device from sleep.",
                "def wake_on_ext0(pin, level) -> None:",
            ],
        ),
    ],
)
def test_rst_parse_function(filename, expected):
    # testcase = FN_1
    r = RSTReader()
    r.read_file(Path(filename))
    # process
    r.parse()
    r.prepare_output()
    # check
    assert len(r.output) > 1
    for fn in expected:
        assert fn in [l.rstrip() for l in r.output]


CLASS_10 = [
    "class Partition:",
    "    def __init__(self, id) -> None:",
    "    @classmethod",
    "    def find(cls, type=TYPE_APP, subtype=0xff, label=None) -> List:",
    #    "    def info(self, ) -> Any:",
    # "    def readblocks(self, block_num, buf) -> Any:",
    # "    def writeblocks(self, block_num, buf) -> Any:",
]


@pytest.mark.parametrize(
    "line",
    [
        "class Partition():",
        "    def __init__(self, id) -> None:",
        "    @classmethod",
        "    def find(cls, type=TYPE_APP, subtype=0xff, label=None) -> List:",
        "    def info(self) -> Tuple:",
        "    def readblocks(self, block_num, buf, offset: Optional[int]=0) -> Any:",
        "    def writeblocks(self, block_num, buf, offset: Optional[int]=0) -> Any:",
    ],
)
# def test_rst_parse_class_10(expected: List[str]):
def test_rst_parse_class_10(line: str):
    # testcase = FN_1
    r = RSTReader()
    r.read_file(Path("tests/rst/data/class_10.rst"))
    # process
    r.parse()
    r.prepare_output()  # cleanup output
    # check if each expected line appears in the output
    # there can be more

    assert len(r.output) > 1
    assert line in [l.rstrip() for l in r.output], f"did not generate : '{line}'"


@pytest.mark.parametrize(
    "param_in, param_out",
    [
        ("", ""),
        ("()", "()"),
        ("() :", "()"),  # strip additional stuff
        ("(\\*, something)", "(*, something)"),  # wrong escaping
        ("([angle])", "(angle: Optional[Any]=None)"),  # simple optional
        ("([angle, time=0])", "(angle: Optional[Any]=None, time=0)"),  # dual optional - hardcoded
        ("('param')", "(param)"),
        (
            "(if_id=0, config=['dhcp' or configtuple])",
            "(if_id=0, config: Union[str,Tuple]='dhcp')",
        ),
        ("lambda)", "lambda_fn)"),
        ("(block_device or path)", "(block_device_or_path)"),
        # network - AbstractNIC.connect
        ("([service_id, key=None, *, ...])", "(service_id, key=None, *args: Optional[Any])"),
        # ("()", "()"),
        # ("()", "()"),
        # ("()", "()"),
    ],
)
def test_fix_param(param_in, param_out):
    "validate known parameter typing notation errors"
    r = RSTReader()
    result = r.fix_parameters(param_in)
    assert result == param_out


def test_import_typing():
    "always include typing"
    r = RSTReader()
    r.prepare_output()
    lines = r.output
    #    lines =
    for line in TYPING_IMPORT:
        assert line.strip() in [l.rstrip() for l in r.output], f"did not import typing : '{line}'"


def test_fix_param_dynamic():
    r = RSTReader()

    # in 'machine' module

    param_in = "(*, trigger, handler=None, wake=machine.IDLE)"
    param_out = "(*, trigger, handler=None, wake=IDLE)"

    # in module
    r.current_module = "machine"
    result = r.fix_parameters(param_in)
    assert result == param_out

    r.current_module = ""
    result = r.fix_parameters(param_in)
    assert result != param_out
    assert result == param_in

    # -----------------------
    param_in = "baudrate=1000000, *, polarity=0, phase=0, bits=8, firstbit=SPI.MSB, sck=None, mosi=None, miso=None)"
    param_out = "baudrate=1000000, *, polarity=0, phase=0, bits=8, firstbit=MSB, sck=None, mosi=None, miso=None)"

    # in class
    r.current_class = "SPI"
    result = r.fix_parameters(param_in)
    assert result == param_out
    # not in class
    r.current_class = ""
    result = r.fix_parameters(param_in)
    assert result != param_out
    assert result == param_in

@pytest.mark.docfix
# @pytest.mark.xfail(reason="upstream docfix needed", condition=XFAIL_DOCFIX)
def test_pyright_Non_default_follows_default(pyright_results, capsys):
    """use pyright to check the validity of the generated stubs
    - Non-default argument follows default argument
    """
    issues: List[Dict] = pyright_results["generalDiagnostics"]
    # workaround : "Non-default argument follows default argument", does not specify rule
    # TODO: apparently the mypy.stubgen does not quite get this right in generating the .pyi
    # , so only flag errors in .py files

    issues = list(
        filter(
            lambda diag: "message" in diag.keys()
            and diag["message"] == "Non-default argument follows default argument"
            and diag["file"].endswith(".py"),
            issues,
        )
    )
    for issue in issues:
        print(f"{issue['message']} in {issue['file']} line {issue['range']['start']['line']}")
    assert len(issues) == 0


# C:\Users\josverl\AppData\Local\Temp\pytest-of-josverl\pytest-143\stubs0\latest\machine.py:778:17 - "MSB" is not defined
# C:\Users\josverl\AppData\Local\Temp\pytest-of-josverl\pytest-143\stubs0\latest\pyb.py:567:46 - "NORMAL" is not defined
# C:\Users\josverl\AppData\Local\Temp\pytest-of-josverl\pytest-143\stubs0\latest\pyb.py:1398:47 - "UP" is not defined
# C:\Users\josverl\AppData\Local\Temp\pytest-of-josverl\pytest-143\stubs0\latest\pyb.py:2244:8 - "hid_mouse" is not defined
# TODO DOCFIX: 
    # wm8960.py
    # SWAP_NONE = 0
    # ROUTE_PLAYBACK_RECORD = 0
    # INPUT_MIC3 = 0
    # INPUT_MIC2 = 0
    # INPUT_MIC2 = 0
    # SYSCLK_MCLK = 0
    # SYNC_DAC = 0
    # BUS_I2S = 1
    # WM8960_I2C_ADDR = 0x1A
    # MUTE_FAST = 0
    # ALC_MODE = 0
@pytest.mark.docfix
@pytest.mark.xfail(reason="upstream docfix needed", condition=XFAIL_DOCFIX)
def test_pyright_undefined_variable(pyright_results, capsys):
    "use pyright to check the validity of the generated stubs"
    issues: List[Dict] = pyright_results["generalDiagnostics"]
    issues = list(filter(lambda diag: "rule" in diag.keys() and diag["rule"] == "reportUndefinedVariable", issues))
    for issue in issues:
        print(f"{issue['file']}:{issue['range']['start']['line']}:{issue['range']['start']['character']} - {issue['message']}  ")
    assert len(issues) == 0, "there should be no `Undefined Variables`"


@pytest.mark.docfix
# @pytest.mark.xfail(reason="upstream docfix needed", condition=XFAIL_DOCFIX)
def test_pyright_reportGeneralTypeIssues(pyright_results, capsys):
    "use pyright to check the validity of the generated stubs - reportGeneralTypeIssues"
    issues: List[Dict] = pyright_results["generalDiagnostics"]
    # workaround : "Non-default argument follows default argument", does not specify rule
    issues = list(
        filter(
            lambda diag: "rule" in diag.keys()
            and diag["rule"] == "reportGeneralTypeIssues"
            and not "is obscured by a declaration" in diag["message"],
            issues,
        )
    )
    for issue in issues:
        print(f"{issue['message']} in {issue['file']} line {issue['range']['start']['line']}")
    # 'Cannot access member "MSB" for type "Type[SPI]" 'Member "MSB" is unknown'
    assert len(issues) <= 1, "There should be no type issues"


@pytest.mark.docfix
# @pytest.mark.xfail(reason="upstream docfix needed", condition=XFAIL_DOCFIX)
def test_pyright_invalid_strings(pyright_results, capsys):
    "use pyright to check the validity of the generated stubs"
    issues: List[Dict] = pyright_results["generalDiagnostics"]

    # Only fail on errors
    issues = list(filter(lambda diag: diag["severity"] == "error", issues))
    issues = list(filter(lambda diag: diag["rule"] == "reportInvalidStringEscapeSequence", issues))
    for issue in issues:
        print(f"{issue['message']} in {issue['file']} line {issue['range']['start']['line']}")
    assert len(issues) == 0, "All strings should be valid"


@pytest.mark.docfix
# @pytest.mark.xfail(reason="upstream docfix needed", condition=XFAIL_DOCFIX)
def test_doc_pyright_obscured_definitions(pyright_results, capsys):

    "use pyright to check the validity of the generated stubs"
    issues: List[Dict] = pyright_results["generalDiagnostics"]
    # Only look at errors
    issues = list(filter(lambda diag: diag["severity"] == "error", issues))
    issues = list(
        filter(
            lambda diag: diag["rule"] == "reportGeneralTypeIssues" and "is obscured by a declaration" in diag["message"],
            issues,
        )
    )
    for issue in issues:
        print(f"{issue['message']} in {issue['file']} line {issue['range']['start']['line']}")

    assert len(issues) == 0, f"There are {len(issues)} function or class defs that obscure earlier defs"


@pytest.mark.docfix
# @pytest.mark.xfail(reason="upstream docfix needed", condition=XFAIL_DOCFIX)
def test_doc_deepsleep_stub(rst_stubs):
    "Deepsleep stub is generated"
    content = read_stub(rst_stubs, "machine.py")
    # return type omitted as this is tested seperately
    found = any(line.startswith("def deepsleep(time_ms") for line in content)
    assert found, "machine.deepsleep should be stubbed as a function, not as a class - Upstream Docfix needed"


# post version 1.16 documentation has been updated usocket.rst -->socket.rst
@pytest.mark.docfix
# @pytest.mark.xfail(reason="upstream docfix needed", condition=XFAIL_DOCFIX)
def test_doc_socket_class_def(rst_stubs: Path):
    "make sense of `usocket.socket` class documented as a function - Upstream Docfix needed"
    content = read_stub(rst_stubs, "usocket.py")
    if content == []:
        # post version 1.16 documentation has been updated usocket.rst -->socket.rst
        content = read_stub(rst_stubs, "socket.py")

    found = any(line.startswith("def socket(") for line in content)
    assert not found, "(u)socket.socket should be stubbed as a class, not as a function"

    found = any(line.startswith("class socket") for line in content)
    assert found, "(u)socket.socket classdef should be generated"

    found = any(line.lstrip().startswith("def __init__(self, af=AF_INET, type=SOCK_STREAM, proto=IPPROTO_TCP") for line in content)
    assert found, "(u)socket.socket __init__ should be generated"


@pytest.mark.parametrize(
    "modulename, classname",
    [
        ("uselect", "poll"),  # compensated
        ("collections", "deque"),
        ("collections", "OrderedDict"),
    ],
)
@pytest.mark.docfix
# @pytest.mark.xfail(reason="upstream docfix needed", condition=XFAIL_DOCFIX)
def test_doc_class_not_function_def(rst_stubs: Path, modulename: str, classname: str):
    "verify `collections.deque` class documented as a function - Upstream Docfix pending"
    filename = modulename + ".py"
    content = read_stub(rst_stubs, filename)
    if content == [] and modulename[0] == "u":
        # module name change to select.py in v1.17+
        filename = filename[1:]
        content = read_stub(rst_stubs, filename)
        if content == []:
            assert f"module {modulename} was not stubbed"
    found = any(line.startswith(f"def {classname}") for line in content)
    # there is actually a poll.poll method ... , so there will be method: def poll ....
    if classname != "poll":
        assert not found, f"class {modulename}.{classname} should not be stubbed as a function"

    found = any(line.startswith(f"class {classname}") for line in content)
    assert found, f"class {modulename}.{classname} must be stubbed as a class"


@pytest.mark.parametrize(
    "error, modulename",
    [
        ('"NORMAL" is not defined', "pyb"),
        ('"UP" is not defined', "pyb.Timer"),
        ('"hid_mouse" is not defined', "pyb.USB_HID"),
        ('"SPI" is not defined', "lcd160cr"),
    ],
)
@pytest.mark.docfix
# @pytest.mark.xfail(reason="upstream docfix needed", condition=XFAIL_DOCFIX)
def test_doc_CONSTANTS(error, modulename, pyright_results, capsys):
    "use pyright to check the validity of the generated stubs"
    issues: List[Dict] = pyright_results["generalDiagnostics"]
    issues = list(
        filter(
            lambda issue: issue["rule"] == "reportUndefinedVariable"
            and issue["message"] == error
            and Path(issue["file"]).stem == modulename,
            issues,
        )
    )
    for issue in issues:
        print(f"{issue['message']} in {issue['file']} line {issue['range']['start']['line']}")
    assert len(issues) == 0
