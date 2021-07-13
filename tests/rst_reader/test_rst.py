# others
import pytest
from pathlib import Path

# SOT
from readfrom_rst import RSTReader, generate_from_rst


def test_rst_all(tmp_path):
    ...
    v_tag = "v1_16"
    rst_folder = Path("micropython/docs/library")
    dst_folder = tmp_path / "noblack"
    x = generate_from_rst(rst_folder, dst_folder, black=False)
    assert type(x) == int, "returns a number"
    assert x > 0, "should generate at least 1 file"

    dst_folder = tmp_path / "black"
    x = generate_from_rst(rst_folder, dst_folder, black=True)
    assert type(x) == int, "returns a number"
    assert x > 0, "should generate at least 1 file"

    # rerun in same folder, same options
    dst_folder = tmp_path / "black"
    x = generate_from_rst(rst_folder, dst_folder, black=True)
    assert type(x) == int, "returns a number"
    assert x > 0, "should generate at least 1 file"


EXP_10 = ["def wake_on_ext0(pin, level) -> Any:", "def wake_on_ext0(pin, level) -> Any:"]


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("tests/rst_reader/data/function_10.rst", EXP_10),
        ("tests/rst_reader/data/function_11.rst", EXP_10),
        ("tests/rst_reader/data/function_12.rst", EXP_10),
        (
            "tests/rst_reader/data/function_12.rst",
            ["        Configure whether or not a touch will wake the device from sleep."],
        ),
    ],
)
def test_rst_parse_function(filename, expected):
    # testcase = FN_1
    r = RSTReader()
    r.read_file(filename)
    # process
    r.parse()
    # check
    assert len(r.output) > 1
    for fn in expected:
        assert fn in [l.rstrip() for l in r.output]


CLASS_10 = [
    "class Partition:",
    "    def __init__(self, id) -> None:",
    "    @classmethod",
    "    def find(cls, type=TYPE_APP, subtype=0xff, label=None) -> Any:",
    #    "    def info(self, ) -> Any:",
    # "    def readblocks(self, block_num, buf) -> Any:",
    # "    def writeblocks(self, block_num, buf) -> Any:",
]


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("tests/rst_reader/data/class_10.rst", CLASS_10),
        ("tests/rst_reader/data/class_10.rst", ["    def info(self, ) -> Any:"]),
        (
            "tests/rst_reader/data/class_10.rst",
            ["    def readblocks(self, block_num, buf) -> Any:"],
        ),
    ],
)
def test_rst_parse_class(filename, expected):
    # testcase = FN_1
    r = RSTReader()
    r.read_file(filename)
    # process
    r.parse()
    # check
    assert len(r.output) > 1
    for line in expected:
        assert line in [l.rstrip() for l in r.output], f"did not generate : '{line}'"


@pytest.mark.parametrize(
    "param_in, param_out",
    [
        ("", ""),
        ("()", "()"),
        ("() :", "()"),  # aditional stuff
        ("(\\*, something)", "(*, something)"),  # wrong escaping
        ("([angle])", "(angle: Optional[Any])"),  # simple optional
        ("([angle, time=0])", "(angle: Optional[Any], time=0)"),  # dual optional - hardcoded
        ("('param')", "(param)"),
        ("(cert_reqs=CERT_NONE)", "(cert_reqs=None)"),
        (
            "(if_id=0, config=['dhcp' or configtuple])",
            "(if_id=0, config: Union[str,Tuple]='dhcp')",
        ),
        ("()", "()"),
        ("()", "()"),
        ("()", "()"),
        ("()", "()"),
        ("()", "()"),
        ("()", "()"),
    ],
)
def test_fix_param(param_in, param_out):
    r = RSTReader()
    result = r.fix_parameters(param_in)
    assert result == param_out


def test_import_typing():
    "always include typing"
    r = RSTReader()
    line = "from typing import Any, Optional, Union, Tuple"
    assert line in [l.rstrip() for l in r.output], f"did not import typing : '{line}'"


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


@pytest.mark.skip(msg="test not yet built")
def test_data_module_level():
    ...


@pytest.mark.skip(msg="test not yet built")
def test_data_class_level():
    ...


@pytest.mark.skip(msg="test not yet built")
def test_exception():
    ...


@pytest.mark.skip(msg="test not yet built")
def test_docstring():
    ...


@pytest.mark.skip(msg="test not yet built")
def test_undocumented_class():
    ...


@pytest.mark.skip(msg="test not yet built")
def test_find_return_type():
    ...


@pytest.mark.skip(msg="test not yet built")
def test_dup_init():
    ...


# Duplicate __init__ FIXME: ucryptolib aes.__init__(key, mode, [IV])


@pytest.mark.skip(msg="test not yet built")
def test_overloaded_defintions():
    ...
