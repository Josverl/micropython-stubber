# .. module:: uerrno
# origin: micropython\docs\library\uerrno.rst
# v1.16
"""
   :synopsis: system error codes

|see_cpython_module| :mod:`python:errno`.

This module provides access to symbolic error codes for `OSError` exception.
A particular inventory of codes depends on :term:`MicroPython port`.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: uerrno
# .. data:: EEXIST, EAGAIN, etc.
# .. data:: errorcode
