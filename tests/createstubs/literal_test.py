# type: ignore reportGeneralTypeIssues
import sys
from collections import namedtuple
from fileinput import filename
from importlib import import_module
from pathlib import Path
from typing import List

import pytest
from mock import MagicMock
from packaging.version import parse
from pytest_mock import MockerFixture

pytestmark = [pytest.mark.stubber]

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib

from shared import LOCATIONS, VARIANTS, import_variant

pytestmark = [pytest.mark.stubber, pytest.mark.micropython]


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("location", LOCATIONS)
def test_get_obj_attributes(
    location,
    variant,
    mock_micropython_path,
):
    createstubs = import_variant(location, variant)

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
def test_literal_order(
    location,
    variant,
    mock_micropython_path,
):
    """
    Literals MUST be listed before methods as they can be used in as defaults in method parameters.
    """
    createstubs = import_variant(location, variant)

    machine = import_module("tests.data.stub_merge.micropython-v1_18-esp32.machine")
    stubber = createstubs.Stubber()  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"

    items, errors = stubber.get_obj_attributes(machine.SoftSPI)
    assert items != []
    # check literals defined before first method
    assert items[0][4] == 1, "Literals MUST be listed before class methods"

    items, errors = stubber.get_obj_attributes(machine)
    assert items != []
    # check literals defined before first method
    assert items[0][4] == 1, "Literals MUST be listed before functions and classes"


@pytest.mark.parametrize("variant", VARIANTS)
def test_literal_init_order(
    variant,
    mock_micropython_path,
    tmp_path,
):
    """
    Literals MUST be listed before methods as they can be used in as defaults in method parameters.
    """
    location = "board"  # no need to test on minified versions
    createstubs = import_variant(location, variant)

    machine = import_module("tests.data.stub_merge.micropython-v1_18-esp32.machine")
    stubber = createstubs.Stubber()  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"

    filename = tmp_path / "test.pyi"
    with open(filename, "w") as f:
        stubber.write_object_stub(f, machine, "", "", 0)

    with open(filename, errors="ignore", encoding="utf8") as f:
        lines = f.readlines()

    lines = [line.rstrip() for line in lines]
    # check literals defined before first method

    class_line = lines.index("class SoftSPI():")
    LSB_line = lines.index("    LSB: int = 1", class_line + 1)
    init_line = lines.index("    def __init__(self, *argv, **kwargs) -> None:", class_line + 1)

    assert class_line < LSB_line < init_line, "Literals MUST be listed before class methods"
