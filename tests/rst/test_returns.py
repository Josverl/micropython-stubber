from typing import List, Tuple
import pytest
from pathlib import Path
import json

# SOT
from stubber.rst.rst_utils import _type_from_context, return_type_from_context

# mark all tests
pytestmark = pytest.mark.doc_stubs


### Test setup
@pytest.mark.parametrize(
    "signature, docstring, expected_type, confidence",
    [
        (".. function:: heap_unlock()", "", "Incomplete", 0),
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
    r = _type_from_context(docstring=docstring, signature=signature, module="builtins")
    assert r["type"] == expected_type
    assert r["confidence"] >= confidence
    t = return_type_from_context(docstring=docstring, signature=signature, module="builtins")
    assert t == expected_type


# read the tests cases from a json file to avoid needing to code all the different tests
def return_type_testcases() -> List[Tuple[str, str, str, str]]:
    filename = Path("./tests/rst/data/return_testcases.json")
    doc = []
    with open(filename, encoding="utf8") as fp:
        doc = json.load(fp)
    cases = []
    for tc in doc:
        try:
            cases.append(
                # (tc["module"], tc["signature"], tc["docstring"], tc["type"], tc["confidence"])
                (tc["type"], tc["module"], tc["signature"], tc["docstring"])
            )
        except KeyError:
            print("INVALID TEST DATA ERROR", tc)
    return cases


# help generate test ids that do not throw bash into a fit
def make_ids(val):
    if isinstance(val, str):
        for c in "()":
            val = val.replace(c, "_")
    return val


@pytest.mark.parametrize("expected_type, module, signature, docstring", return_type_testcases(), ids=make_ids)
def test_returns(module, signature, docstring, expected_type):
    # return type should be included in the signature
    # except for classes
    # confidence = 0.1
    r = _type_from_context(docstring=docstring, signature=signature, module=module)
    assert r["type"] == expected_type
    # assert r["confidence"] >= confidence
    t = return_type_from_context(docstring=docstring, signature=signature, module=module)
    assert t == expected_type
