# others
from typing import Dict, List, Union
import pytest
from pathlib import Path
import basicgit as git

# SOT
from readfrom_rst import generate_from_rst, RSTReader, TYPING_IMPORT


from helpers import load_rst, read_stub

####################################################################################################

MODULE_DOCSTR = """
:mod:`uhashlib` -- hashing algorithms
=====================================

.. module:: uhashlib
:synopsis: hashing algorithms

|see_cpython_module| :mod:`python:hashlib`.

This module implements binary data hashing algorithms. The exact inventory
of available algorithms depends on a board. Among the algorithms which may
be implemented:

* SHA256 - The current generation, modern hashing algorithm (of SHA2 series).
It is suitable for cryptographically-secure purposes. Included in the
MicroPython core and any board is recommended to provide this, unless
it has particular code size constraints.

* SHA1 - A previous generation algorithm. Not recommended for new usages,
but SHA1 is a part of number of Internet standards and existing
applications, so boards targeting network connectivity and
interoperability will try to provide this.

* MD5 - A legacy algorithm, not considered cryptographically secure. Only
selected boards, targeting interoperability with legacy applications,
will offer this.

Constructors
------------
"""

CLASS_DOCSTR = """
"""

QUOTED_DOCSTR = """
.. data:: MONO_VLSB
:     Monochrome (1-bit) color format
:     This defines a mapping where the bits in a byte are vertically mapped with
:     bit 0 being nearest the top of the screen. Consequently each byte occupies
:     8 vertical pixels. Subsequent bytes appear at successive horizontal
:     locations until the rightmost edge is reached. Further bytes are rendered
:     at locations starting at the leftmost edge, 8 pixels lower.
.. data:: MONO_HLSB
+     Monochrome (1-bit) color format
+     This defines a mapping where the bits in a byte are horizontally mapped.
+     Each byte occupies 8 horizontal pixels with bit 7 being the leftmost.
+     Subsequent bytes appear at successive horizontal locations until the
+     rightmost edge is reached. Further bytes are rendered on the next row, one
+     pixel lower.
"""


def test_parse_docstr_module():
    # check if the module name has been removed form the class def
    r = RSTReader()
    load_rst(r, MODULE_DOCSTR)
    # r.current_module = module # 'uhashlib'
    # process
    r.parse()
    # check
    assert len(r.output) > 1
    assert len(r.output_dict["docstr"]) > 20

    # start & end with triple Quote
    assert r.output_dict["docstr"][0] == '"""'
    assert r.output_dict["docstr"][-1] == '"""'

    # don't care about indentation
    # assert line.strip() in [l.strip() for l in r.output]


def test_parse_docstr_quoted():
    # quoted docstrings from module level constants
    r = RSTReader()
    load_rst(r, QUOTED_DOCSTR)
    r.parse()
    # check
    assert len(r.output) > 1
    assert len(r.output_dict["constants"]) > 2

    assert not any(
        [l.startswith("# :") for l in r.output_dict["constants"]]
    ), "Some lines were not unquoted"
    assert not any(
        [l.startswith("# +") for l in r.output_dict["constants"]]
    ), "Some lines were not unquoted"
