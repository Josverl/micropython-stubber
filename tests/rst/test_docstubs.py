from pathlib import Path

import pytest

# SOT
from stubber.stubs_from_docs import make_docstub


def test_make_docstub(tmp_path, pytestconfig):
    "network.rst has a toc on in middle of the file, and that stopped the parse."
    rst = pytestconfig.rootpath / "tests/rst/data/network.rst"
    # Create a temporary file to simulate the docstub creation
    version = "v1.25.0"
    result = make_docstub(
        file=rst,
        dst_path=tmp_path,
        v_tag=version,
        release=version,
        suffix=".pyi",
        clean_rst=True,
    )

    expected_lines = [
        "class AbstractNIC(Protocol):",
        "def country(code: Optional[Any]=None) -> Incomplete:",
        "def hostname(name: Optional[Any]=None) -> Incomplete:",
        "def ipconfig(param:Optional[str]=None, *args, **kwargs) -> str:",
    ]
    # Read the content of the generated docstub file
    docstub_file = tmp_path / "network/__init__.pyi"
    with open(docstub_file, "r") as f:
        content = f.readlines()
    # Check if the expected lines are in the content
    for line in expected_lines:
        assert any(line in content_line for content_line in content), f"Expected line '{line}' not found in docstub content."
