from typing import Dict, List, Tuple
import pytest
from pathlib import Path
import json

# SOT
from rst_utils import type_from_docstring


### Test setup
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


# read the tests cases from a json file to avoid needing to code all the different tests
def return_type_testcases() -> List[Tuple[str, str, str, int]]:
    filename = Path("./tests/rst_reader/data/return_testcases.json")
    doc = []
    with open(filename, encoding="utf8") as fp:
        doc = json.load(fp)
    cases = []
    for tc in doc:
        cases.append((tc["signature"], tc["docstring"], tc["type"], tc["confidence"]))
    return cases


@pytest.mark.parametrize("sig, docstr, exp, conf", return_type_testcases())
def test_returns(sig, docstr, exp, conf):
    # return type should be included in the signature
    # except for classes
    r = type_from_docstring(docstr, sig)
    assert r["type"] == exp
    assert r["confidence"] >= conf
