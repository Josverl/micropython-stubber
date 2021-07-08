# .. module:: ujson
# origin: micropython\docs\library\ujson.rst
# v1.16
"""
   :synopsis: JSON encoding and decoding

|see_cpython_module| :mod:`python:json`.

This modules allows to convert between Python objects and the JSON
data format.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: ujson
# .. function:: dump(obj, stream)
def dump(obj, stream) -> Any:
    """
    Serialise *obj* to a JSON string, writing it to the given *stream*.
    """
    ...


# .. function:: load(stream)
def load(stream) -> Any:
    """
    Parse the given *stream*, interpreting it as a JSON string and
    deserialising the data to a Python object.  The resulting object is
    returned.

    Parsing continues until end-of-file is encountered.
    A :exc:`ValueError` is raised if the data in *stream* is not correctly formed.
    """
    ...
