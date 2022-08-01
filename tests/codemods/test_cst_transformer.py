from typing import NamedTuple, Tuple

import libcst
import pytest

import difflib
import sys

from stubber.cst_transformer import StubMergeTransformer

from .codemodcollector import (
    TestCase,
    collect_test_cases,
)


@pytest.mark.parametrize("test_case", collect_test_cases())
def test_merge(test_case: TestCase) -> None:
    "test merging of firmwarestubs with docstubs using libcst"

    if "_skip" in str(test_case.path):
        pytest.skip("Skipping test because of _skip")
    elif "import_" in str(test_case.path):
        pytest.skip("Skipping import test as they cannot be dealth with")
    elif "_xfail" in str(test_case.path):
        pytest.xfail("xfail")

    source_tree = libcst.parse_module(test_case.before)

    # create transformer for this stubfile
    transformer = StubMergeTransformer(stub=test_case.stub)
    # apply the stub transformer to the source tree
    merged_tree = source_tree.visit(transformer)

    # note: test must deal with differences in code formatting /black formatting
    # Todo : format with usort // black ?
    # https://ufmt.omnilib.dev/en/stable/

    # write to output file if specified in test_case
    if test_case.output:
        with open(test_case.output, "w") as file:
            file.write(merged_tree.code)

    if not merged_tree.code == test_case.after:
        delta = difflib.unified_diff(
            merged_tree.code.splitlines(keepends=True),
            test_case.after.splitlines(keepends=True),
            fromfile="merged",
            tofile="expected after.py",
        )
        print("".join(delta))

    assert merged_tree.code == test_case.after
