from typing import Dict, List, Tuple, Any
import pytest
from pathlib import Path
import json

# SOT
from readfrom_rst import generate_from_rst, RSTReader, TYPING_IMPORT

from rst.utils import _type_from_context, return_type_from_context

#: Use this content as input for moo to do bar
# FOOBAR: Any = 1


SEQ_NUMBERS = [
    ".. data:: UINT8\n",
    "          INT8\n",
    "          UINT16\n",
    "          INT16\n",
    "          UINT32\n",
    "          INT32\n",
    "          UINT64\n",
    "          INT64\n",
    "\n",
    "   Integer types for structure descriptors. Constants for 8, 16, 32,\n",
    "   and 64 bit types are provided, both signed and unsigned.\n",
    "\n",
]

SEQ_2 = """
Constants
~~~~~~~~~

.. data:: Partition.BOOT
          Partition.RUNNING

    Used in the `Partition` constructor to fetch various partitions: ``BOOT`` is the
    partition that will be booted at the next reset and ``RUNNING`` is the currently
    running partition.

.. data:: Partition.TYPE_APP
          Partition.TYPE_DATA

    Used in `Partition.find` to specify the partition type: ``APP`` is for bootable
    firmware partitions (typically labelled ``factory``, ``ota_0``, ``ota_1``), and
    ``DATA`` is for other partitions, e.g. ``nvs``, ``otadata``, ``phy_init``, ``vfs``.

.. data:: HEAP_DATA
          HEAP_EXEC

    Used in `idf_heap_info`.
"""


def test_number_sequence():
    testcase = SEQ_NUMBERS
    r = RSTReader()
    # Plug in test data
    # r.rst_text = SEQ_NUMBERS
    r.rst_text = testcase
    r.filename = "testdata.py"
    r.current_module = "testdata"
    r.max_line = len(r.rst_text) - 1
    # process
    r.parse()
    # check
    assert len(r.output) > 1
    constants = len([l for l in r.output_dict["constants"] if not l.startswith("# ")])
    assert constants == 8


def test_comma_sequence():
    SEQ_COMMAS = [
        ".. data:: EEXIST, EAGAIN, etc.\n",
        "     Error codes, based on ANSI C/POSIX standard. All error codes start with\n",
        "     'E'. As mentioned above,\n",
    ]

    r = RSTReader()
    # Plug in test data
    # r.rst_text = SEQ_NUMBERS
    r.rst_text = SEQ_COMMAS
    r.filename = "testdata.py"
    r.current_module = "testdata"
    r.max_line = len(r.rst_text) - 1
    # process
    r.parse()

    # check that etc is not found
    etc = "etc. : Any\n" in r.output
    eexist = "EEXIST : Any\n" in r.output
    eagain = "EAGAIN : Any\n" in r.output
    assert not etc
    assert eexist
    assert eagain


SEQ_3 = """
.. class:: framebuf() 

.. data:: framebuf.MONO_VLSB
:     Monochrome (1-bit) color format
:     This defines a mapping where the bits in a byte are vertically mapped with
:     bit 0 being nearest the top of the screen. Consequently each byte occupies
:     8 vertical pixels. Subsequent bytes appear at successive horizontal
:     locations until the rightmost edge is reached. Further bytes are rendered
:     at locations starting at the leftmost edge, 8 pixels lower.
.. data:: framebuf.MONO_HLSB
:     Monochrome (1-bit) color format
:     This defines a mapping where the bits in a byte are horizontally mapped.
:     Each byte occupies 8 horizontal pixels with bit 7 being the leftmost.
:     Subsequent bytes appear at successive horizontal locations until the
:     rightmost edge is reached. Further bytes are rendered on the next row, one
:     pixel lower.
.. data:: framebuf.MONO_HMSB
:     Monochrome (1-bit) color format
:     This defines a mapping where the bits in a byte are horizontally mapped.
:     Each byte occupies 8 horizontal pixels with bit 0 being the leftmost.
:     Subsequent bytes appear at successive horizontal locations until the
:     rightmost edge is reached. Further bytes are rendered on the next row, one
:     pixel lower.
.. data:: framebuf.RGB565
:     Red Green Blue (16-bit, 5+6+5) color format
.. data:: framebuf.GS2_HMSB
:     Grayscale (2-bit) color format
.. data:: framebuf.GS4_HMSB
:     Grayscale (4-bit) color format
.. data:: framebuf.GS8
:     Grayscale (8-bit) color format
"""


def test_sequence_3():

    r = RSTReader()
    # Plug in test data
    # r.rst_text = SEQ_NUMBERS
    r.rst_text = SEQ_3.splitlines(keepends=True)
    r.filename = "testdata.py"
    r.current_module = "testdata"
    r.max_line = len(r.rst_text) - 1
    # process
    r.parse()

    assert len(r.output) > 1
    c_list = r.output_dict["class framebuf():"]["constants"]
    constants = len([l for l in c_list if not l.lstrip().startswith("# ")])
    assert constants == 7

