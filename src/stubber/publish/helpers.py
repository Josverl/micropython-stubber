"""
This module provides a function to retrieve the docstring of a Python module.
"""

from pathlib import Path
from typing import Any, Union

import libcst as cst


def get_module_docstring(fname: Path) -> Union[str, Any]:
    """
    Retrieve the docstring of a Python module.

    Args:
        fname (Path): The path to the Python module file.

    Returns:
        Union[str, Any]: The docstring of the Python module, or None if no docstring is found.
    """
    try:
        with open(fname, "r") as file:
            content = file.read()
        mod = cst.parse_module(content)
        return mod.get_docstring()
    except Exception as e:
        print(e)
        return None

