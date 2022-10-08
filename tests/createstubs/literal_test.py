# type: ignore reportGeneralTypeIssues
import sys
from collections import namedtuple
from importlib import import_module
from pathlib import Path
from typing import List

import pytest
from mock import MagicMock
from packaging.version import parse
from pytest_mock import MockerFixture

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib

from conftest import LOCATIONS, VARIANTS

pytestmark = pytest.mark.micropython


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_get_obj_attributes(
    location,
    variant,
    mock_micropython_path,
):
    createstubs = import_module(f"{location}.{variant}")  # type: ignore

    stubber = createstubs.Stubber()  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    items, errors = stubber.get_obj_attributes(sys)
    assert items != []
    assert errors == []
    assert len(items) > 50
    for attr in items:
        assert type(attr) == tuple


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_literal_ordering(
    location,
    variant,
    mock_micropython_path,
):
    """
    Literals MUST be listed before methods as they can be used in as defaults in method parameters.
    """
    global FIRST_VERSION

    createstubs = import_module(f"{location}.{variant}")  # type: ignore

    stubber = createstubs.Stubber()  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    items, errors = stubber.get_obj_attributes(sys)
    assert items != []

    # check literals defined before first method
