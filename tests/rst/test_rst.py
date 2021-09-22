# others
from typing import Dict, List, Union
import pytest
from pathlib import Path
import basicgit as git

from helpers import load_rst, read_stub

# SOT
from readfrom_rst import generate_from_rst, RSTReader, TYPING_IMPORT


MICROPYTHON_FOLDER = "micropython"


###################################################################################################
# Fixtures for re-use by different test methods
# shared across this module
###################################################################################################
@pytest.fixture(scope="module")
def pyright(rst_stubs):
    "Run pyright over folder with rst generated stubs, and return the results"

    # cmd = ["pyright", "generated/micropython/1_16-nightly", "--outputjson"]
    cmd = ["pyright", rst_stubs.as_posix(), "--outputjson"]
    try:
        # result = subprocess.run(cmd, capture_output=False)
        result = subprocess.run(cmd, capture_output=True)
    except OSError as e:
        raise e
    results = json.loads(result.stdout)
    assert results["summary"]["filesAnalyzed"] >= 40, ">= 40 files checked"
    yield results
    # cleanup code here


@pytest.fixture(scope="module")
def micropython_repo():
    "make sure a recent branch is checked out"
    git.switch_branch("master", MICROPYTHON_FOLDER)
    TEST_DOCFIX = True
    if TEST_DOCFIX:
        # run test against the proposed documentation fixes
        try:
            git.switch_branch("fix_lib_documentation", MICROPYTHON_FOLDER)
        except Exception:
            git.switch_branch("master", MICROPYTHON_FOLDER)

    v_tag = git.get_tag(MICROPYTHON_FOLDER) or "xx_x"
    yield v_tag


# TODO: Source version and tag
@pytest.fixture(scope="module")
def rst_stubs(tmp_path_factory: pytest.TempPathFactory, micropython_repo):
    "Generate stubs from RST files - once for this module"
    v_tag = micropython_repo
    # setup our on folder for testing
    dst_folder = tmp_path_factory.mktemp("stubs") / v_tag
    rst_folder = Path(MICROPYTHON_FOLDER) / "docs/library"
    x = generate_from_rst(rst_folder, dst_folder, v_tag=v_tag, black=True)
    yield dst_folder
    # cleanup code here


###################################################################################################
#
###################################################################################################


def test_rst_all(tmp_path, micropython_repo):
    v_tag = micropython_repo

    rst_folder = Path(MICROPYTHON_FOLDER) / "docs/library"
    dst_folder = tmp_path / "noblack"
    x = generate_from_rst(rst_folder, dst_folder, v_tag=v_tag, black=False)
    assert type(x) == int, "returns a number"
    assert x > 0, "should generate at least 1 file"

    dst_folder = tmp_path / "black"
    x = generate_from_rst(rst_folder, dst_folder, v_tag=v_tag, black=True)
    assert type(x) == int, "returns a number"
    assert x > 0, "should generate at least 1 file"

    # rerun in same folder, same options
    dst_folder = tmp_path / "black"
    x = generate_from_rst(rst_folder, dst_folder, v_tag=v_tag, black=True)
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
        "    def readblocks(self, block_num, buf) -> Any:",
        "    def writeblocks(self, block_num, buf) -> Any:",
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
        ("([angle])", "(angle: Optional[Any])"),  # simple optional
        ("([angle, time=0])", "(angle: Optional[Any], time=0)"),  # dual optional - hardcoded
        ("('param')", "(param)"),
        ("(cert_reqs=CERT_NONE)", "(cert_reqs=None)"),
        (
            "(if_id=0, config=['dhcp' or configtuple])",
            "(if_id=0, config: Union[str,Tuple]='dhcp')",
        ),
        ("lambda)", "lambda_fn)"),
        ("(block_device or path)", "(block_device_or_path)"),
        # ("()", "()"),
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


import subprocess
import json


# @pytest.mark.xfail(reason="code to be written")
def test_pyright_undefined_variable(pyright, capsys):
    "use pyright to check the validity of the generated stubs"
    issues: List[Dict] = pyright["generalDiagnostics"]
    issues = list(filter(lambda diag: diag["rule"] == "reportUndefinedVariable", issues))
    with capsys.disabled():
        for issue in issues:
            print(f"{issue['message']} in {issue['file']} line {issue['range']['start']['line']}")
    assert len(issues) == 0, "there should be no `Undefined Variables`"


def test_pyright_reportGeneralTypeIssues(pyright, capsys):
    "use pyright to check the validity of the generated stubs - reportGeneralTypeIssues"
    issues: List[Dict] = pyright["generalDiagnostics"]
    issues = list(
        filter(
            lambda diag: diag["rule"] == "reportGeneralTypeIssues"
            and not "is obscured by a declaration" in diag["message"],
            issues,
        )
    )
    with capsys.disabled():
        for issue in issues:
            print(f"{issue['message']} in {issue['file']} line {issue['range']['start']['line']}")
    # TODO: 1 known issue
    # 'Cannot access member "MSB" for type "Type[SPI]" 'Member "MSB" is unknown'
    assert len(issues) == 1, "there should be no type issues"


def test_pyright_invalid_strings(pyright, capsys):
    "use pyright to check the validity of the generated stubs"
    issues: List[Dict] = pyright["generalDiagnostics"]

    # Only fail on errors
    issues = list(filter(lambda diag: diag["severity"] == "error", issues))
    issues = list(filter(lambda diag: diag["rule"] == "reportInvalidStringEscapeSequence", issues))
    with capsys.disabled():
        for issue in issues:
            print(f"{issue['message']} in {issue['file']} line {issue['range']['start']['line']}")
    assert len(issues) == 0, "all string should be valid"


@pytest.mark.xfail(reason="upstream docfix needed")
def test_doc_pyright_obscured_definitions(pyright, capsys):
    "use pyright to check the validity of the generated stubs"
    issues: List[Dict] = pyright["generalDiagnostics"]
    # Only look at errors
    issues = list(filter(lambda diag: diag["severity"] == "error", issues))
    issues = list(
        filter(
            lambda diag: diag["rule"] == "reportGeneralTypeIssues"
            and "is obscured by a declaration" in diag["message"],
            issues,
        )
    )
    with capsys.disabled():
        for issue in issues:
            print(f"{issue['message']} in {issue['file']} line {issue['range']['start']['line']}")
    # TODO:  ure.py 'Function declaration "match" is obscured by a declaration of the same name'
    assert len(issues) == 1, f"There are {len(issues)} redefinitions that obscure earlier defs"


@pytest.mark.xfail(reason="upstream docfix needed")
def test_doc_deepsleep_stub(rst_stubs):
    "Deepsleep stub is generated"
    content = read_stub(rst_stubs, "machine.py")
    # return type omitted as this is tested seperately
    found = any("def deepsleep(time_ms: Optional[Any]) -> " in line for line in content)
    assert (
        found
    ), "machine.deepsleep should be stubbed as a function, not as a class - Upstream Docfix needed"
    # # .. function:: deepsleep([time_ms])
    # def deepsleep(time_ms: Optional[Any]) -> xxx:


# post version 1.16 documentation has been updated usocket.rst -->socket.rst
@pytest.mark.xfail(reason="upstream docfix needed")
def test_doc_socket_class_def(rst_stubs: Path):
    "make sense of `usocket.socket` class documented as a function - Upstream Docfix needed"
    content = read_stub(rst_stubs, "usocket.py")
    if content == []:
        # post version 1.16 documentation has been updated usocket.rst -->socket.rst
        content = read_stub(rst_stubs, "socket.py")

    found = any("def socket(" in line for line in content)
    assert not found, "(u)socket.socket should be stubbed as a class, not as a function"

    found = any("class socket:" in line for line in content)
    assert found, "(u)socket.socket classdef should be generated"

    found = any(
        "def __init__(self, af=AF_INET, type=SOCK_STREAM, proto=IPPROTO_TCP, /) -> None:" in line
        for line in content
    )
    assert found, "(u)socket.socket __init__ should be generated"


@pytest.mark.xfail(reason="upstream docfix needed")
def test_doc_poll_class_def(rst_stubs: Path):
    "make sense of `uselect.socket` class documented as a function - Upstream Docfix pending"
    content = read_stub(rst_stubs, "uselect.py")

    found = any("def poll()" in line for line in content)
    assert not found, "uselect.poll class should not be stubbed as a function"

    found = any("class poll:" in line for line in content)
    assert found, "uselect.poll should be stubbed as a class"


# def socket(af=AF_INET, type=SOCK_STREAM, proto=IPPROTO_TCP, /) -> Any:
