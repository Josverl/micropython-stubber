"""pytest fixtures for publish tests"""

import shutil
from pathlib import Path

import pytest
from pysondb import PysonDB
from pytest_mock import MockerFixture

from stubber.publish.enums import COMBO_STUBS
from stubber.publish.package import create_package

from .fakeconfig import FakeConfig


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
    pkg = create_package("micropython-fake-stubs", mpy_version=version, port="esp32", pkg_type=COMBO_STUBS)
    pkg._publish = False
    pkg.create_license()
    pkg.create_readme()
    yield pkg


@pytest.fixture
def temp_db(
    pytestconfig: pytest.Config,
    tmp_path: Path,
):
    """"""
    db_src = pytestconfig.rootpath / "tests/publish/data/package_data_test.jsondb"
    db_path = tmp_path / "package_data_test.jsondb"
    # copy file to temp location
    shutil.copy(db_src, db_path)
    db = PysonDB(db_path.as_posix())

    def fake_commit():
        pass

    db.commit = fake_commit
    yield db
