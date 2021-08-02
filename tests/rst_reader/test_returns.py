from typing import Dict, List, Tuple
import pytest
from pathlib import Path
import json

# SOT
from rst_utils import type_from_docstring


### Test setup
@pytest.mark.parametrize(
    "signature, docstring, expected_type, confidence",
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
def test_signatures(signature, docstring, expected_type, confidence):
    # return type should be included in the signature
    # except for classes
    r = type_from_docstring(docstring, signature, "builtins")
    assert r["type"] == expected_type
    assert r["confidence"] >= confidence


# read the tests cases from a json file to avoid needing to code all the different tests
def return_type_testcases() -> List[Tuple[str, str, str, str, int]]:
    filename = Path("./tests/rst_reader/data/return_testcases.json")
    doc = []
    with open(filename, encoding="utf8") as fp:
        doc = json.load(fp)
    cases = []
    for tc in doc:
        try:
            cases.append(
                (tc["module"], tc["signature"], tc["docstring"], tc["type"], tc["confidence"])
            )
        except KeyError:
            print("INVALID TEST DATA ERROR", tc)
    return cases


@pytest.mark.parametrize(
    "module, signature, docstring, expected_type, confidence", return_type_testcases()
)
def test_returns(module, signature, docstring, expected_type, confidence):
    # return type should be included in the signature
    # except for classes
    r = type_from_docstring(docstring, signature, module)
    assert r["type"] == expected_type
    assert r["confidence"] >= confidence
