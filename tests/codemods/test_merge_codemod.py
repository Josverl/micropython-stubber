from typing import NamedTuple, Tuple

import libcst
import pytest

# from tornado_async_transformer import TornadoAsyncTransformer
from .codemodcollector import (
    TestCase,
    collect_test_cases,
)


@pytest.mark.parametrize("test_case", collect_test_cases())
def test_merge(test_case: TestCase) -> None:
    ""test merging of firmwarestubs with docstubs using libcst"
    source_tree = libcst.parse_module(test_case.before)
    visited_tree = source_tree
    # visited_tree = source_tree.visit(TornadoAsyncTransformer())
    assert visited_tree.code == test_case.after
