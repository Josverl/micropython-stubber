from typing import Dict, List
import pytest
from pathlib import Path

# SOT
from rst_utils import type_from_docstring


@pytest.mark.parametrize(
    "sig, docstr, exp, conf",
    [
        (".. function:: heap_unlock()", "", "Any", 0),
        (".. function:: heap_unlock()->None", "", "None", 1),
        (".. function:: heap_unlock()->None:", "", "None", 1),
        (".. function:: heap_unlock()->None: ", "", "None", 1),
        (".. function:: heap_unlock()->None : ", "", "None", 1),
        (".. function:: heap_unlock()->List[str] : ", "", "List[str]", 1),
        #        (".. class:: heap_unlock()->str : ", "", "None", 1),
    ],
)
def test_signatures(sig, docstr, exp, conf):
    # return type should be included in the signature
    # except for classes
    r = type_from_docstring(docstr, sig)
    assert r["type"] == exp
    assert r["confidence"] >= conf
