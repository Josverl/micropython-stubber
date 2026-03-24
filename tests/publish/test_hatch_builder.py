"""Tests for HatchBuilder and package_type support in StubPackage."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from stubber.publish.enums import PackageType, StubSource
from stubber.publish.package import create_package
from stubber.publish.stubpackage import HatchBuilder, PoetryBuilder, StubPackage
from stubber.utils.config import CONFIG

from .fakeconfig import FakeConfig

pytestmark = [pytest.mark.stubber]


# -------------------------------------------------------------------------
# PackageType enum
# -------------------------------------------------------------------------


def test_package_type_values():
    assert PackageType.POETRY.value == "poetry"
    assert PackageType.HATCH.value == "hatch"


def test_package_type_str():
    assert str(PackageType.POETRY) == "poetry"
    assert str(PackageType.HATCH) == "hatch"


def test_package_type_from_str():
    assert PackageType("poetry") == PackageType.POETRY
    assert PackageType("hatch") == PackageType.HATCH


# -------------------------------------------------------------------------
# StubPackage default package_type (poetry, backward compat)
# -------------------------------------------------------------------------


@pytest.mark.parametrize("version, port, board", [("v1.24.1", "rp2", "RPI_PICO")])
def test_stub_package_default_package_type(tmp_path, pytestconfig, version, port, board, mocker):
    """StubPackage must default to poetry for backward compatibility."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=Path("./repos/micropython-stubs/stubs"),
        template_path=pytestconfig.rootpath / "tests/publish/data/template",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    pkg = create_package(f"micropython-{port}-stubs", mpy_version=version, port=port, board=board)
    assert isinstance(pkg, StubPackage)
    assert pkg.package_type == PackageType.POETRY


# -------------------------------------------------------------------------
# HatchBuilder – create_update_pyproject_toml
# -------------------------------------------------------------------------


@pytest.mark.parametrize("version, port, board", [("v1.24.1", "rp2", "RPI_PICO")])
def test_hatch_package_creates_pyproject(tmp_path, pytestconfig, version, port, board, mocker):
    """StubPackage with package_type='hatch' should create a hatchling pyproject.toml."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=Path("./repos/micropython-stubs/stubs"),
        template_path=pytestconfig.rootpath / "tests/publish/data/template",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    pkg = create_package(
        f"micropython-{port}-stubs",
        mpy_version=version,
        port=port,
        board=board,
        package_type=PackageType.HATCH,
    )
    assert isinstance(pkg, StubPackage)
    assert pkg.package_type == PackageType.HATCH

    toml_path = pkg.package_path / "pyproject.toml"
    assert toml_path.exists(), "pyproject.toml should be created"

    pyproject = pkg.pyproject
    assert pyproject is not None

    # hatchling build system
    build_sys = pyproject.get("build-system", {})
    assert "hatchling" in build_sys.get("requires", []), "hatchling must be listed in build-system.requires"
    assert build_sys.get("build-backend") == "hatchling.build"

    # project metadata
    assert pyproject["project"]["name"] == f"micropython-{port}-stubs"


# -------------------------------------------------------------------------
# HatchBuilder – update_pyproject_stubs adds include list
# -------------------------------------------------------------------------


def test_hatch_update_pyproject_stubs(tmp_path, pytestconfig, mocker):
    """update_pyproject_stubs for hatch should populate tool.hatch.build.targets.wheel.include."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=Path("./repos/micropython-stubs/stubs"),
        template_path=pytestconfig.rootpath / "tests/publish/data/template",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    pkg = create_package("micropython-esp32-stubs", mpy_version="v1.24.1", port="esp32", package_type=PackageType.HATCH)

    # Write some fake .pyi files into the package path
    pkg.package_path.mkdir(parents=True, exist_ok=True)
    (pkg.package_path / "machine.pyi").write_text("# stub")
    (pkg.package_path / "os.pyi").write_text("# stub")

    count = pkg.update_pyproject_stubs()
    assert count == 2

    pyproject = pkg.pyproject
    assert pyproject is not None
    include = pyproject["tool"]["hatch"]["build"]["targets"]["wheel"]["include"]
    assert "machine.pyi" in include
    assert "os.pyi" in include


# -------------------------------------------------------------------------
# PoetryBuilder – update_pyproject_stubs unchanged
# -------------------------------------------------------------------------


def test_poetry_update_pyproject_stubs(tmp_path, pytestconfig, mocker):
    """update_pyproject_stubs for poetry should populate tool.poetry.packages."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=Path("./repos/micropython-stubs/stubs"),
        template_path=pytestconfig.rootpath / "tests/publish/data/template",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    pkg = create_package("micropython-esp32-stubs", mpy_version="v1.24.1", port="esp32", package_type=PackageType.POETRY)

    pkg.package_path.mkdir(parents=True, exist_ok=True)
    (pkg.package_path / "machine.pyi").write_text("# stub")

    count = pkg.update_pyproject_stubs()
    assert count >= 1

    pyproject = pkg.pyproject
    assert pyproject is not None
    packages = pyproject["tool"]["poetry"]["packages"]
    assert any("machine.pyi" in str(p) for p in packages)


# -------------------------------------------------------------------------
# pkg_version setter / getter for hatch packages
# -------------------------------------------------------------------------


def test_hatch_pkg_version_roundtrip(tmp_path, pytestconfig, mocker):
    """pkg_version getter/setter should work for hatch packages using [project] section."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=Path("./repos/micropython-stubs/stubs"),
        template_path=pytestconfig.rootpath / "tests/publish/data/template",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    pkg = create_package("micropython-esp32-stubs", mpy_version="v1.24.1", port="esp32", package_type=PackageType.HATCH)

    pkg.pkg_version = "1.24.1.post5"
    assert pkg.pkg_version == "1.24.1.post5"


# -------------------------------------------------------------------------
# create_update_pyproject_toml idempotency (hatch)
# -------------------------------------------------------------------------


def test_hatch_create_update_idempotent(tmp_path, pytestconfig, mocker):
    """Calling create_update_pyproject_toml twice for hatch should not raise."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=Path("./repos/micropython-stubs/stubs"),
        template_path=pytestconfig.rootpath / "tests/publish/data/template",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    pkg = create_package("micropython-esp32-stubs", mpy_version="v1.24.1", port="esp32", package_type=PackageType.HATCH)

    # Second call should not raise
    pkg.create_update_pyproject_toml()

    pyproject = pkg.pyproject
    assert pyproject is not None
    assert pyproject["project"]["name"] == "micropython-esp32-stubs"


# -------------------------------------------------------------------------
# package_type=hatch accepted as str ("hatch")
# -------------------------------------------------------------------------


def test_stub_package_accepts_str_package_type(tmp_path, pytestconfig, mocker):
    """StubPackage should accept package_type as a plain string."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=Path("./repos/micropython-stubs/stubs"),
        template_path=pytestconfig.rootpath / "tests/publish/data/template",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    pkg = StubPackage("micropython-esp32-stubs", "esp32", version="1.24.1", package_type="hatch")
    assert pkg.package_type == PackageType.HATCH


# -------------------------------------------------------------------------
# check() for HatchBuilder
# -------------------------------------------------------------------------


def test_hatch_check(tmp_path, pytestconfig, mocker):
    """HatchBuilder.check() returns True when pyproject.toml exists."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=Path("./repos/micropython-stubs/stubs"),
        template_path=pytestconfig.rootpath / "tests/publish/data/template",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    pkg = create_package("micropython-esp32-stubs", mpy_version="v1.24.1", port="esp32", package_type=PackageType.HATCH)
    assert (pkg.package_path / "pyproject.toml").exists()
    assert HatchBuilder.check(pkg) is True  # type: ignore[arg-type]


# -------------------------------------------------------------------------
# CONFIG.package_type drives the default
# -------------------------------------------------------------------------


def test_config_package_type_is_default():
    """CONFIG.package_type should be the canonical default (poetry by default)."""
    assert isinstance(CONFIG.package_type, PackageType)
    # The default shipped in config is PackageType.POETRY
    assert CONFIG.package_type == PackageType.POETRY


def test_stub_package_uses_config_default(tmp_path, pytestconfig, mocker):
    """When no package_type is supplied, StubPackage uses CONFIG.package_type."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=Path("./repos/micropython-stubs/stubs"),
        template_path=pytestconfig.rootpath / "tests/publish/data/template",
    )
    # Override the config used by StubPackage AND the one used as the default
    # argument value (CONFIG.package_type in the function signature).
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)
    mocker.patch("stubber.publish.package.CONFIG", config)

    # config.package_type is PackageType.POETRY (the FakeConfig default)
    pkg = create_package("micropython-esp32-stubs", mpy_version="v1.24.1", port="esp32")
    assert pkg.package_type == config.package_type


# -------------------------------------------------------------------------
# Database: package_type stored and restored
# -------------------------------------------------------------------------


def test_to_dict_includes_package_type(tmp_path, pytestconfig, mocker):
    """to_dict() must include the package_type key."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=Path("./repos/micropython-stubs/stubs"),
        template_path=pytestconfig.rootpath / "tests/publish/data/template",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    pkg = create_package("micropython-esp32-stubs", mpy_version="v1.24.1", port="esp32", package_type=PackageType.HATCH)
    d = pkg.to_dict()
    assert "package_type" in d
    assert d["package_type"] == "hatch"


def test_from_dict_restores_package_type(tmp_path, pytestconfig, mocker):
    """from_dict() must restore package_type from the stored value."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=Path("./repos/micropython-stubs/stubs"),
        template_path=pytestconfig.rootpath / "tests/publish/data/template",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    json_data = {
        "name": "micropython-esp32-stubs",
        "port": "esp32",
        "board": "GENERIC",
        "variant": "",
        "mpy_version": "1.24.1",
        "publish": True,
        "pkg_version": "1.24.1.post1",
        "path": "micropython-v1_24_1-esp32-stubs",
        "stub_sources": "[]",
        "description": "test",
        "hash": "",
        "stub_hash": "",
        "package_type": "hatch",
    }
    pkg = StubPackage("micropython-esp32-stubs", "esp32", version="1.24.1", json_data=json_data)
    assert pkg.package_type == PackageType.HATCH


def test_from_dict_missing_package_type_infers_from_toml(tmp_path, pytestconfig, mocker):
    """When package_type is absent from DB row, infer from the on-disk pyproject.toml."""
    config = FakeConfig(
        publish_path=tmp_path / "publish",
        stub_path=Path("./repos/micropython-stubs/stubs"),
        template_path=pytestconfig.rootpath / "tests/publish/data/template",
    )
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    # First create a hatch package so a hatch-style pyproject.toml is on disk
    hatch_pkg = create_package("micropython-esp32-stubs", mpy_version="v1.24.1", port="esp32", package_type=PackageType.HATCH)
    assert (hatch_pkg.package_path / "pyproject.toml").exists()

    # Now load from a "legacy" DB row (no package_type key) — should infer HATCH
    json_data = {
        "name": "micropython-esp32-stubs",
        "port": "esp32",
        "board": "GENERIC",
        "variant": "",
        "mpy_version": "1.24.1",
        "publish": True,
        "pkg_version": "1.24.1.post1",
        "path": hatch_pkg.package_path.name,
        "stub_sources": "[]",
        "description": "test",
        "hash": "",
        "stub_hash": "",
        # package_type intentionally absent
    }
    pkg2 = StubPackage("micropython-esp32-stubs", "esp32", version="1.24.1", json_data=json_data)
    assert pkg2.package_type == PackageType.HATCH


def test_database_migration_adds_column(tmp_path):
    """Opening an old DB (no package_type column) should add the column automatically."""
    import sqlite3
    from stubber.publish.database import create_database, _migrate_add_package_type

    # Create an old-style database without the package_type column
    old_db_path = tmp_path / "data" / "all_packages_test.db"
    old_db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(old_db_path)
    conn.execute(
        """
        CREATE TABLE "packages" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, description TEXT, mpy_version TEXT, pkg_version TEXT,
            publish BOOLEAN, stub_sources TEXT, path TEXT, hash TEXT,
            stub_hash TEXT, port TEXT DEFAULT "", board TEXT DEFAULT "",
            variant TEXT DEFAULT ""
        )
        """
    )
    conn.commit()

    # Migration should add the column
    _migrate_add_package_type(conn)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(packages)")
    columns = {row[1] for row in cursor.fetchall()}
    assert "package_type" in columns
    conn.close()
