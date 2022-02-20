# others
from typing import Dict, List, Union
import pytest
from pathlib import Path
import stubber.basicgit as git

# SOT
from stubber.stubs_from_docs import generate_from_rst, RSTReader, TYPING_IMPORT


from helpers import load_rst, read_stub

MACHINE_RST = """
:mod:`machine` --- functions related to the hardware
====================================================

.. module:: machine
   :synopsis: functions related to the hardware

The ``machine`` module contains specific functions related to the hardware

.. function:: rng()

   Return a 24-bit software generated random number.

   Availability: WiPy.

.. _machine_constants:

Constants
---------

.. data:: machine.IDLE
          machine.SLEEP
          machine.DEEPSLEEP

    IRQ wake values.

.. data:: machine.PWRON_RESET
          machine.HARD_RESET
          machine.WDT_RESET
          machine.DEEPSLEEP_RESET
          machine.SOFT_RESET

    Reset causes.

.. data:: machine.WLAN_WAKE
          machine.PIN_WAKE
          machine.RTC_WAKE

    Wake-up reasons.
"""

MACHINE_PIN_RST = """
Constructors
------------

.. class:: Pin(id, mode=-1, pull=-1, *, value, drive, alt)

   Access the pin peripheral (GPIO pin) associated with the given ``id``.  If
   additional arguments are given in the constructor then they are used to initialise
   the pin.  Any settings that are not specified will remain in their previous state.

Constants
---------

The following constants are used to configure the pin objects.  Note that
not all constants are available on all ports.

.. data:: Pin.IN
          Pin.OUT
          Pin.OPEN_DRAIN
          Pin.ALT
          Pin.ALT_OPEN_DRAIN

   Selects the pin mode.

.. data:: Pin.PULL_UP
          Pin.PULL_DOWN
          Pin.PULL_HOLD

   Selects whether there is a pull up/down resistor.  Use the value
   ``None`` for no pull.

.. data:: Pin.LOW_POWER
          Pin.MED_POWER
          Pin.HIGH_POWER

   Selects the pin drive strength.

.. data:: Pin.IRQ_FALLING
          Pin.IRQ_RISING
          Pin.IRQ_LOW_LEVEL
          Pin.IRQ_HIGH_LEVEL

   Selects the IRQ trigger type.

.. data:: Pin.JOKER_*

   Test wildcard handling.

"""


def test_module_constants():
    # test is module level constants can be processed
    r = RSTReader()
    load_rst(r, MACHINE_RST)
    r.current_module = "machine"
    # process
    r.parse()
    # check
    assert len(r.output) > 1
    list = r.output_dict["constants"]
    doc_list = [c for c in list if c.startswith("#")]
    const_list = [c for c in list if not c.startswith("#")]
    # should have 11  constants
    assert len(const_list) == 11
    # and 11 single line comments for docstrings
    assert len(doc_list) == 11


def test_class_constants():
    # check if the module name has been removed form the class def
    r = RSTReader()
    load_rst(r, MACHINE_PIN_RST)
    # r.current_module = module # 'uhashlib'
    # process
    r.parse()
    # check
    assert len(r.output) > 1
    expected = [
        "class Pin():",
        "    #    Selects the pin mode.",
        "    IN : Any = ...",
        "    OPEN_DRAIN : Any = ...",
        "    #    Test wildcard handling.",
        "    # JOKER_* : Any = ...",
        "    def __init__(self, id, mode=-1, pull=-1, *, value=None, drive=0, alt=-1) -> None:",
    ]
    lines = [l.rstrip() for l in r.output]
    for l in expected:
        assert l in lines
