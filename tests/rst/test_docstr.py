# others
import pytest

# SOT
from stubber.rst.reader import RSTWriter

from helpers import load_rst

# mark all tests
pytestmark = [pytest.mark.stubber, pytest.mark.doc_stubs]


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
    r = RSTWriter()
    load_rst(r, MODULE_DOCSTR)
    # r.current_module = module # 'uhashlib'
    # process
    r.parse()
    r.prepare_output()
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
    r = RSTWriter()
    load_rst(r, QUOTED_DOCSTR)
    r.parse()
    r.prepare_output()
    # check
    assert len(r.output) > 1
    assert len(r.output_dict["constants"]) > 2

    assert not any(l.startswith("# :") for l in r.output_dict["constants"]), "Some lines were not unquoted"
    assert not any(l.startswith("# +") for l in r.output_dict["constants"]), "Some lines were not unquoted"


## method is broken over two lines
PYB_CAN_DOCSTR = """
.. currentmodule:: pyb
.. _pyb.CAN:

class CAN -- controller area network communication bus
======================================================

CAN implements support for classic CAN (available on F4, F7 MCUs) and CAN FD (H7 series) controllers.

The following CAN module functions and their arguments are available
for both classic and FD CAN controllers, unless otherwise stated.

Constructors
------------

.. class:: pyb.CAN(bus, ...)

   Construct a CAN object on the given bus.  *bus* can be 1-2, or ``'YA'`` or ``'YB'``.

Methods
-------

.. method:: CAN.init(mode, prescaler=100, *, sjw=1, bs1=6, bs2=8, auto_restart=False, baudrate=0, sample_point=75,
        num_filter_banks=14, brs_sjw=1, brs_bs1=8, brs_bs2=3, brs_baudrate=0, brs_sample_point=75)

   Initialise the CAN bus with the given parameters:


.. method:: CAN.multi(mode, prescaler=100, *, sjw=1, 
        bs1=6, bs2=8, auto_restart=False, baudrate=0, sample_point=75,
        num_filter_banks=14, brs_sjw=1, brs_bs1=8, brs_bs2=3, brs_baudrate=0, 
        brs_sample_point=75)

   Initialise the CAN bus with the given parameters:


"""


def test_parse_long_method():
    r = RSTWriter()
    load_rst(r, PYB_CAN_DOCSTR)
    r.parse()
    r.prepare_output()
    # check
    assert len(r.output) > 1
    assert r.output_dict
    assert r.output_dict["class CAN():"]

    assert r.output_dict["class CAN():"]["def init"]
    # closing bracket in first line of method def
    assert ")" in r.output_dict["class CAN():"]["def init"]["def"][0]

    assert r.output_dict["class CAN():"]["def multi"]
    # closing bracket in first line of method def
    assert ")" in r.output_dict["class CAN():"]["def multi"]["def"][0]
