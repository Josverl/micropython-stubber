"""Test publish module - refactored"""
from pathlib import Path
import pytest
from mock import MagicMock
from pytest_mock import MockerFixture
from packaging.version import parse


from stubber.publish.stubpacker import StubPackage
from pysondb import PysonDB


@pytest.mark.mocked
@pytest.mark.integration
def test_hash(
    mocker: MockerFixture, tmp_path: Path, pytestconfig: pytest.Config, fake_package: StubPackage
):
    pkg = fake_package

    pkg.update_package_files()
    stub_count = pkg.update_included_stubs()
    assert stub_count > 0

    calc_hash_md = pkg.calculate_hash(include_md=True)
    calc_hash_pyi = pkg.calculate_hash(include_md=False)

    # both should be present
    assert calc_hash_md
    assert calc_hash_pyi
    assert calc_hash_pyi != calc_hash_md, "hashes should be different"

    changed_after_update = pkg.is_changed()
    assert changed_after_update, "should be changed initially"

    pkg.update_hashes()
    assert pkg.hash
    assert pkg.stub_hash
    assert pkg.hash != pkg.stub_hash, "hashes should be different"

    # check that the hashes are correct
    assert pkg.hash == calc_hash_md
    assert pkg.stub_hash == calc_hash_pyi

    # should not register as changed after update
    changed_after_update = pkg.is_changed()
    assert not changed_after_update, "should not show as changed after update"

    # TEST CHANGE DETECTION
    # change the hash
    pkg.hash = "1234567890"
    assert pkg.is_changed(), "should show as changed after hash change"

    # change the stub hash
    pkg.hash = calc_hash_md
    pkg.stub_hash = "1234567890"
    assert pkg.is_changed(include_md=False), "should show as changed after stub hash change"


@pytest.mark.integration
def test_update_package(fake_package: StubPackage):
    pkg = fake_package

    changed_after_update = pkg.is_changed()
    assert changed_after_update, "should be changed initially"

    ok = pkg.update_package(production=True)
    assert ok, "should be ok"

    changed_after_update = pkg.is_changed()
    assert changed_after_update, "should be changed after update"

    calc_hash_md = pkg.calculate_hash(include_md=True)
    calc_hash_pyi = pkg.calculate_hash(include_md=False)

    # both should be present
    assert calc_hash_md
    assert calc_hash_pyi
    assert calc_hash_pyi != calc_hash_md, "hashes should be different"

    pkg.update_hashes()
    assert pkg.hash
    assert pkg.stub_hash
    assert pkg.hash != pkg.stub_hash, "hashes should be different"

    # should not register as changed after update
    changed_after_update = pkg.is_changed()
    assert not changed_after_update, "should not show as changed after update"

    # can the hashes be saved to the database
    db_dict = pkg.to_dict()
    assert db_dict
    assert db_dict["hash"]
    assert db_dict["stub_hash"]

    assert db_dict["hash"] == calc_hash_md
    assert db_dict["stub_hash"] == calc_hash_pyi

    assert db_dict["hash"] != db_dict["stub_hash"], "hashes should be different"


@pytest.mark.integration
def test_build_package(
    mocker: MockerFixture, tmp_path: Path, pytestconfig: pytest.Config, fake_package: StubPackage
):
    pkg = fake_package

    result = pkg.build(production=False, force=False)

    assert result, "should be ok"

    # check if the package was built
    dist_path = pkg.package_path / "dist"
    assert dist_path.exists(), "dist path should exist"
    assert dist_path.is_dir(), "dist path should be a directory"
    # check if the dist path contains a wheel
    assert len(list(dist_path.glob("*.whl"))) == 1, "should be one wheel in the dist path"
    assert len(list(dist_path.glob("*.gz"))) == 1, "should be one tarball in the dist path"
    # package still should show as changed in order to trigger a publish
    assert pkg.is_changed(), "should show as changed after build"


@pytest.mark.integration
def test_publish_package(
    mocker: MockerFixture,
    tmp_path: Path,
    pytestconfig: pytest.Config,
    fake_package: StubPackage,
    temp_db: PysonDB,
):
    pkg = fake_package
    db = temp_db

    m_publish: MagicMock = mocker.patch(
        "stubber.publish.package.StubPackage.poetry_publish", autospec=True, return_value=True
    )

    # allow the publishing logic to run during test
    pkg._publish = True  # type: ignore
    result = pkg.publish(production=False, force=False, db=db)

    assert result, "should be ok"

    # check if the package was built
    dist_path = pkg.package_path / "dist"
    assert dist_path.exists(), "dist path should exist"
    assert dist_path.is_dir(), "dist path should be a directory"
    # check if the dist path contains a wheel
    assert len(list(dist_path.glob("*.whl"))) == 1, "should be one wheel in the dist path"
    assert len(list(dist_path.glob("*.gz"))) == 1, "should be one tarball in the dist path"

    assert not pkg.is_changed(), "should show as un changed after publish"

    # Check if the  has been published
    assert m_publish.called, "should call poetry publish"

    # check is the hashes are added to the database
    recs = db.get_by_query(
        query=lambda x: x["mpy_version"] == pkg.mpy_version and x["name"] == pkg.package_name
    )
    # dict to list
    recs = [{"id": key, "data": recs[key]} for key in recs]
    # sort
    packages = sorted(recs, key=lambda x: parse(x["data"]["pkg_version"]))

    assert packages[-1]["data"]["name"] == pkg.package_name, "should be the same package name"
    assert (
        packages[-1]["data"]["pkg_version"] == pkg.pkg_version
    ), "should be the same package version"
    assert packages[-1]["data"]["mpy_version"] == pkg.mpy_version, "should be the same mpy version"
    assert packages[-1]["data"]["hash"] == pkg.hash, "should be the same hash"
    assert packages[-1]["data"]["stub_hash"] == pkg.stub_hash, "should be the same stub hash"
