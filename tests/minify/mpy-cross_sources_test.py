from io import BytesIO, StringIO
from pathlib import Path
import pytest

from stubber.minify import cross_compile

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

# test cross compile with different sources and targets
# sources:                  Targets
# - file                    Path(folder), Path(file)
# - string
# -
def test_xc_file_folder(tmp_path: Path, pytestconfig: pytest.Config):
    "file -> folder"
    source = "createstubs.py"
    source_path = pytestconfig.rootpath / "src" / "stubber" / "board" / source
    result = cross_compile(source=source_path, target=tmp_path)
    assert result == 0

    # there should be a .mpy file in the folder
    assert len(list(tmp_path.glob("*.mpy"))) == 1


def test_xc_file_file(tmp_path: Path, pytestconfig: pytest.Config):
    "file -> file"
    source = "createstubs.py"
    source_path = pytestconfig.rootpath / "src" / "stubber" / "board" / source
    result = cross_compile(source=source_path, target=tmp_path / "test.mpy")
    assert result == 0
    # there should be a .mpy file in the folder
    assert len(list(tmp_path.glob("test.mpy"))) == 1


def test_xc_str_to_folder(tmp_path: Path, pytestconfig: pytest.Config):
    "string -> folder"
    result = cross_compile(source=SOURCE, target=tmp_path)
    assert result == 0
    # there should be a .mpy file in the folder
    assert len(list(tmp_path.glob("*.mpy"))) == 1


def test_xc_str_to_file(tmp_path: Path, pytestconfig: pytest.Config):
    "string -> file"
    ret = cross_compile(source=SOURCE, target=tmp_path / "test.mpy")
    assert ret == 0
    # there should be a .mpy file in the folder
    assert len(list(tmp_path.glob("test.mpy"))) == 1


def test_xc_str_to_bytesio(tmp_path: Path, pytestconfig: pytest.Config):
    "string -> folder"
    target = BytesIO()
    ret = cross_compile(source=SOURCE, target=target)
    assert ret == 0
    result = target.getvalue()
    target.close()
    assert len(result) > 0


def test_xc_strio_to_bytesio(tmp_path: Path, pytestconfig: pytest.Config):
    "string IO  -> Bytes IO"
    target = BytesIO()
    source = StringIO(initial_value=SOURCE)
    ret = cross_compile(source=source, target=target)
    assert ret == 0
    result = target.getvalue()
    target.close()
    assert len(result) > 0
