"""pytest fixtures for publish tests"""

import shutil
import sqlite3
from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from stubber.publish.package import create_package

from .fakeconfig import FakeConfig

pytestmark = [pytest.mark.stubber]


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
def temp_db_conn(
    pytestconfig: pytest.Config,
    tmp_path: Path,
):
    """"""
    db_src = pytestconfig.rootpath / "tests/publish/data/all_packages_test.db"
    db_path = tmp_path / "all_packages_test.db"
    # copy file to temp location
    shutil.copy(db_src, db_path)

    db_conn = sqlite3.connect(db_path)
    db_conn.row_factory = sqlite3.Row # return rows as dicts
    yield db_conn
    try:
        db_conn.close()
        db_path.unlink()
    except Exception as e:
        pass
