from typing import Dict, List, Tuple, Any
import pytest
from pathlib import Path
import json

# SOT
from readfrom_rst import generate_from_rst, RSTReader, TYPING_IMPORT

from rst_utils import _type_from_context, return_type_from_context

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

SEQ_NUMBERS_2 = [
    "Constants\n",
    "~~~~~~~~~\n",
    "\n",
    ".. data:: Partition.BOOT\n",
    "          Partition.RUNNING\n",
    "\n",
    "    Used in the `Partition` constructor to fetch various partitions: ``BOOT`` is the\n",
    "    partition that will be booted at the next reset and ``RUNNING`` is the currently\n",
    "    running partition.\n",
    "\n",
    ".. data:: Partition.TYPE_APP\n",
    "          Partition.TYPE_DATA\n",
    "\n",
    "    Used in `Partition.find` to specify the partition type: ``APP`` is for bootable\n",
    "    firmware partitions (typically labelled ``factory``, ``ota_0``, ``ota_1``), and\n",
    "    ``DATA`` is for other partitions, e.g. ``nvs``, ``otadata``, ``phy_init``, ``vfs``.\n",
    "\n",
    ".. data:: HEAP_DATA\n",
    "          HEAP_EXEC\n",
    "\n",
    "    Used in `idf_heap_info`.\n",
]


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
