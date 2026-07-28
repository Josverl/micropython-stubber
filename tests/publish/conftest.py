"""pytest fixtures for publish tests"""

import shutil
import sqlite3
from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from stubber.publish.database import _migrate_add_package_type
from stubber.publish.package import create_package

from .fakeconfig import FakeConfig

pytestmark = [pytest.mark.stubber]


# Stub source folders referenced by the packages exercised in the publish tests.
# They are copied into an isolated temp stub path so the tests never depend on -
# or write to - the real ``repos/micropython-stubs`` checkout.
ISOLATED_STUB_SOURCES = [
    "micropython-core",
    "micropython-v1_18-esp32-merged",
    "micropython-v1_18-frozen/esp32/GENERIC",
    "micropython-v1_20_0-rp2-PICO-merged",
    "micropython-v1_20_0-frozen/rp2/GENERIC",
    "micropython-v1_22_1-rp2-RPI_PICO-merged",
]


@pytest.fixture
def isolated_publish_config(mocker: MockerFixture, tmp_path: Path, pytestconfig: pytest.Config):
    """Redirect publish/stub/template paths to an isolated temp location.

    Prevents tests that build packages from writing ``pyproject.toml`` (or any
    other file) into the real ``repos/micropython-stubs`` checkout. A small set
    of stub source folders is copied into the temp stub path so source/combo
    resolution has real folders to find.
    """
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    real_stubs = pytestconfig.rootpath / "repos/micropython-stubs/stubs"
    config.stub_path = tmp_path / "stubs"
    config.stub_path.mkdir(parents=True, exist_ok=True)
    for rel in ISOLATED_STUB_SOURCES:
        src = real_stubs / rel
        if src.exists():
            dst = config.stub_path / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst, dirs_exist_ok=True)

    mocker.patch("stubber.publish.publish.CONFIG", config)
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)
    mocker.patch("stubber.publish.package.CONFIG", config)
    return config



@pytest.fixture
def fake_package(request, mocker: MockerFixture, tmp_path: Path, pytestconfig: pytest.Config):
    """\
        Create a fake package for testing
        - use the test config
        - use specified version or defaults to 1.19.1
        - specify version using a marker: @pytest.mark.version("1.20.0")
        
        """
    # use the test config - in two places
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.publish.CONFIG", config)
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)
    if "version" in request.keywords:
        # use specified version
        version = request.keywords["version"].args[0]
    else:
        # use default version
        version = "1.19.1"
    pkg = create_package("micropython-fake-stubs", mpy_version=version, port="esp32")
    pkg._publish = False  # type: ignore
    pkg.create_license()
    pkg.create_readme()
    yield pkg


@pytest.fixture
def test_db_conn(
    pytestconfig: pytest.Config,
    tmp_path: Path,
):
    """"""
    db_src = pytestconfig.rootpath / "tests/publish/data/test_packages.db"
    db_path = tmp_path / "all_packages_test.db"
    # copy file to temp location
    shutil.copy(db_src, db_path)

    db_conn = sqlite3.connect(db_path)
    db_conn.row_factory = sqlite3.Row  # return rows as dicts
    _migrate_add_package_type(db_conn)  # ensure schema is up to date
    yield db_conn
    try:
        db_conn.close()
        db_path.unlink()
    except Exception as e:
        pass
