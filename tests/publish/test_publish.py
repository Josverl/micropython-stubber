"""Test publish module - refactored"""

import sqlite3
from pathlib import Path

import pytest
from mock import MagicMock
from pytest_mock import MockerFixture
from stubber.publish.stubpackage import StubPackage

pytestmark = [pytest.mark.stubber]


@pytest.mark.mocked
@pytest.mark.integration
def test_hash(
    mocker: MockerFixture, tmp_path: Path, pytestconfig: pytest.Config, fake_package: StubPackage
):
    pkg = fake_package

    pkg.update_package_files()
    stub_count = pkg.update_pyproject_stubs()
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
    # FIXME± this has a dpendency on a connection to PyPI.org
    ok = pkg.update_distribution(production=True)
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
    # FIXME: dependency on online test.pypi.org
    result = pkg.build_distribution(production=False, force=False)

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
    test_db_conn: sqlite3.Connection,
):
    pkg = fake_package

    m_publish: MagicMock = mocker.patch(
        "stubber.publish.package.StubPackage.poetry_publish", autospec=True, return_value=True
    )

    # allow the publishing logic to run during test
    pkg._publish = True  # type: ignore

    # FIXME : dependency to access to test.pypi.org
    result = pkg.publish_distribution_ifchanged(
        production=False, force=False, db_conn=test_db_conn
    )

    assert result, "should be ok"

    # check if the package was built
    dist_path = pkg.package_path / "dist"
    assert dist_path.exists(), "dist path should exist"
    assert dist_path.is_dir(), "dist path should be a directory"
    # check if the dist path contains a wheel
    assert len(list(dist_path.glob("*.whl"))) == 1, "should be one wheel in the dist path"
    assert len(list(dist_path.glob("*.gz"))) == 1, "should be one tarball in the dist path"

    assert not pkg.is_changed(), "should show as unchanged after publish"

    # Check if the  has been published
    assert m_publish.called, "should call poetry publish"

    # check is the hashes are added to the database
    cursor = test_db_conn.cursor()
    cursor.execute(
        "SELECT * FROM packages where name = ? AND mpy_version = ? ORDER by pkg_version DESC",
        (pkg.package_name, pkg.mpy_version),
    )
    recs = cursor.fetchall()

    row = recs[0]
    assert row["name"] == pkg.package_name, "should be the same package name"
    assert row["port"] == pkg.port, "should be the same port"
    assert row["board"] == pkg.board, "should be the same board"
    assert row["variant"] == pkg.variant, "should be the same variant"

    assert row["pkg_version"] == pkg.pkg_version, "should be the same package version"
    assert row["mpy_version"] == pkg.mpy_version, "should be the same mpy version"
    assert row["hash"] == pkg.hash, "should be the same hash"
    assert row["stub_hash"] == pkg.stub_hash, "should be the same stub hash"
