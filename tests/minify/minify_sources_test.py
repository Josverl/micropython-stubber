from io import StringIO
from pathlib import Path
from typing import List
import pytest
from stubber.minify import minify

# mark all tests
pytestmark = pytest.mark.minify

SOURCE = '''
"""
Create stubs for (all) modules on a MicroPython board
"""
# Copyright (c) 2019-2022 Jos Verlinde
# pylint: disable= invalid-name, missing-function-docstring, import-outside-toplevel, logging-not-lazy
import gc
import logging
import sys

import uos as os
from ujson import dumps
print("test")

x = 1
'''

# test minify with different sources and targets
# sources:              Targets:
# - file                Path
# - string              StringIO
# - stringIO
def test_minify_file_to_folder(tmp_path: Path, pytestconfig: pytest.Config):
    "file -> folder"
    source = "createstubs.py"
    source_path = pytestconfig.rootpath / "src" / "stubber" / "board" / source
    result = minify(source=source_path, target=tmp_path)
    assert result == 0
    # now test that log statements have been removed
    with open(tmp_path / source) as f:
        content = f.readlines()
    check_results(content)


def test_minify_str_to_folder(tmp_path: Path, pytestconfig: pytest.Config):
    """string -> folder"""

    result = minify(source=SOURCE, target=tmp_path)
    assert result == 0
    # now test that log statements have been removed
    with open(tmp_path / "minified.py") as f:
        content = f.readlines()
    check_results(content)


def test_minify_str_to_strio(tmp_path: Path, pytestconfig: pytest.Config):
    "string -> file in folder"
    target = StringIO()
    ret = minify(source=SOURCE, target=target)
    assert ret == 0
    result = target.getvalue()
    target.close()
    content = result.splitlines()
    check_results(content)


def test_minify_strio_to_strio(tmp_path: Path, pytestconfig: pytest.Config):
    "string -> file in folder"
    source = StringIO(initial_value=SOURCE)
    target = StringIO()
    ret = minify(source=source, target=target)
    assert ret == 0
    result = target.getvalue()
    target.close()
    content = result.splitlines()
    check_results(content)


def check_results(content: List[str]):
    for line in content:
        assert line.find("._log") == -1, "Failed: all references to ._log have been removed"
    # # not sure why this was/is needed 
    # check if there is a line with 'import gc'
    # assert any(line.find("import gc") != -1 for line in content), "failed: gc is still imported"
    # assert any(line.find("from ujson import dumps") != -1 for line in content), "failed: dumps is still imported"
