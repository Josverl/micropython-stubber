from pathlib import Path

import pytest

from stubber.modcat import STDLIB_SHADOWING_MODULES, package_stub_destination


def test_stdlib_shadow_inventory_is_complete():
    assert len(STDLIB_SHADOWING_MODULES) == 35


@pytest.mark.parametrize(
    ("source", "destination"),
    [
        ("time.pyi", "stdlib/time.pyi"),
        ("html/__init__.pyi", "stdlib/html/__init__.pyi"),
        ("html/parser.pyi", "stdlib/html/parser.pyi"),
        ("string/__init__.pyi", "stdlib/string/__init__.pyi"),
        ("machine.pyi", "machine.pyi"),
        ("aioble/core.pyi", "aioble/core.pyi"),
    ],
)
def test_package_stub_destination(source: str, destination: str):
    assert package_stub_destination(Path(source)) == Path(destination)
