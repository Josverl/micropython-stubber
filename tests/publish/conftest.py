"""pytest fixtures for publish tests"""

from pathlib import Path
import shutil
import pytest
from pytest_mock import MockerFixture

from .fakeconfig import FakeConfig


from stubber.publish.enums import COMBO_STUBS
from pysondb import PysonDB


@pytest.fixture
def fake_package(mocker: MockerFixture, tmp_path: Path, pytestconfig: pytest.Config):
    # use the test config - in two places
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.publish.CONFIG", config)
    mocker.patch("stubber.publish.stubpacker.CONFIG", config)
    version = "1.19.1"
    pkg = create_package("micropython-fake-stubs",  mpy_version = version,  port="esp32", pkg_type=COMBO_STUBS)
    pkg._publish = False
    pkg.create_license()
    pkg.create_readme()
    yield pkg

@pytest.fixture
def temp_db( pytestconfig: pytest.Config, tmp_path: Path, ):
    ""
    db_src = pytestconfig.rootpath / "tests/publish/data/package_data_test.jsondb"
    db_path = tmp_path / "package_data_test.jsondb"
    # copy file to temp location
    shutil.copy(db_src, db_path)
    db = PysonDB(db_path.as_posix())
    def fake_commit():
        pass
    db.commit = fake_commit
    yield db
