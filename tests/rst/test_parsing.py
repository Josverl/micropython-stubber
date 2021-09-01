# others
from typing import Dict, List, Union
import pytest
from pathlib import Path
import basicgit as git

# SOT
from readfrom_rst import generate_from_rst, RSTReader, TYPING_IMPORT


from helpers import load_rst, read_stub

####################################################################################################


CD_ACCEL = """
    .. _pyb.Accel:

    class Accel -- accelerometer control
    ====================================

    Accel is an object that controls the accelerometer.  Example usage::

        accel = pyb.Accel()
        for i in range(10):
            print(accel.x(), accel.y(), accel.z())

    Raw values are between -32 and 31.


    Constructors
    ------------

    .. class:: pyb.Accel()

    Create and return an accelerometer object.

    Methods
    -------

    .. method:: Accel.filtered_xyz()

    Get a 3-tuple of filtered x, y and z values.

    Implementation note: this method is currently implemented as taking the
    sum of 4 samples, sampled from the 3 previous calls to this function along
    with the sample from the current call.  Returned values are therefore 4
    times the size of what they would be from the raw x(), y() and z() calls.
"""

CD_HASHLIB = """
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

    .. class:: uhashlib.sha256([data])

        Create an SHA256 hasher object and optionally feed ``data`` into it.

    .. class:: uhashlib.sha1([data])

        Create an SHA1 hasher object and optionally feed ``data`` into it.

    .. class:: uhashlib.md5([data])

        Create an MD5 hasher object and optionally feed ``data`` into it.

"""
# @pytest.mark.parametrize(
@pytest.mark.parametrize(
    "line",
    [
        "class Accel:",
        "    def __init__(self) -> None:",
        "    def filtered_xyz(self) -> Tuple:",
    ],
)
@pytest.mark.parametrize(
    "module",
    [
        "pyb",
        "upyb",
    ],
)
def test_parse_class_modulename(line, module):
    # check if the module name has been removed form the class def
    r = RSTReader()
    load_rst(r, CD_ACCEL)
    r.current_module = module
    # process
    r.parse()
    r._cleanup()
    # check
    assert len(r.output) > 1
    expected = []
    assert line in [l.rstrip() for l in r.output]


@pytest.mark.parametrize(
    "line",
    [
        "class sha1:",
        "class sha256:",
        "class md5:",
    ],
)
def test_parse_class_micro_modulename(line):
    # check if the module name has been removed form the class def
    r = RSTReader()
    load_rst(r, CD_HASHLIB)
    # r.current_module = module # 'uhashlib'
    # process
    r.parse()
    r._cleanup()
    # check
    assert len(r.output) > 1
    expected = []
    # don't care about indentation
    assert line.strip() in [l.strip() for l in r.output]


@pytest.mark.skip(reason="test not yet built")
def test_dup_init():
    #  classes with multiple __init__ methods
    # Duplicate __init__ FIXME: ucryptolib aes.__init__(key, mode, [IV])
    ...


@pytest.mark.skip(reason="test not yet built")
def test_Flash_init_overload():
    # "pyb.Flash_init_overload is generated"
    # class Flash:
    #     """
    #     :noindex:
    #     Create and return a block device that accesses the flash at the specified offset. The length defaults to the remaining size of the device.
    #     The *start* and *len* offsets are in bytes, and must be a multiple of the block size (typically 512 for internal flash).
    #     """
    #     def __init__(self, *, start=-1, len=-1) -> None:
    ...


@pytest.mark.skip(reason="test not yet built")
def test_data_module_level():
    "all modules should have a docstring"
    ...


@pytest.mark.skip(reason="test not yet built")
def test_data_class_level():
    "all classes should have a docstring"
    ...


@pytest.mark.skip(reason="test not yet built")
def test_exception():
    # exception:: AssertionError
    ...


@pytest.mark.skip(reason="test not yet built")
def test_undocumented_class():
    # percentage of classes with docstring
    # list classes without a docstring
    # >> similar for function / methods
    ...


@pytest.mark.skip(reason="test not yet built")
def test_find_return_type():
    # check return types for a number of known functions / methods
    # check % return type !=  Any ?
    ...


@pytest.mark.skip(reason="test not yet built")
def test_coroutine():
    # {
    #     "signature": "start_server(callback, host, port, backlog=5)",
    #     "docstring": [
    #         "    Start a TCP server on the given *host* and *port*.  The *callback* will be",
    #         "    called with incoming, accepted connections, and be passed 2 arguments: reader",
    #         "    and writer streams for the connection.",
    #         "",
    #         "    Returns a `Server` object.",
    #         "",
    #         "    This is a coroutine."
    #     ],
    #     "docstring_len": 257,
    #     "type": "Server",
    #     "confidence": 1.37052,
    #     "match": "<re.Match object; span=(209, 234), match='Returns a `Server` object'>",
    #     "module": "uasyncio",
    #     "class": "",
    #     "function/method": "start_server"
    # }
    # https://docs.python.org/3.5/library/typing.html#typing.Coroutine
    ...
