from pathlib import Path
import stubber
from packaging.version import parse

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib


def test_package_versions_are_in_sync():
    """Checks if the pyproject.toml and package.__init__.py __version__ are in sync."""
    # Q&D Location
    path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = tomllib.loads(open(str(path)).read())
    pyproject_version = pyproject["tool"]["poetry"]["version"]

    package_init_version = stubber.__version__

    assert parse(package_init_version).public == parse(pyproject_version).public
