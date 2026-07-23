from pathlib import Path

import pytest
from packaging.version import parse

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore
assert tomllib  # - one out of two will work
import stubber

pytestmark = [pytest.mark.stubber]


def test_package_versions_are_in_sync():
    """Checks if the pyproject.toml and package.__init__.py __version__ are in sync."""
    # Q&D Location
    path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = tomllib.loads(open(str(path)).read())
    # version is dynamic (hatchling reads it from stubber.__version__);
    # the bump-my-version config tracks the same value across all managed files.
    pyproject_version = pyproject["tool"]["bumpversion"]["current_version"]

    package_init_version = stubber.__version__

    assert parse(pyproject_version).public.startswith(parse(package_init_version).public)
