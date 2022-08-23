import os
import shutil
from contextlib import contextmanager
from pathlib import Path

import pytest
import stubber.publish.stubpacker as stubpacker
from stubber.publish.publish_stubs import (
    ALL_TYPES,
    COMBO_STUBS,
    CORE_STUBS,
    DOC_STUBS,
    create_package,
    get_database,
    get_package_info,
    package_name,
)

# # use our test paths
# stubpacker.PUBLISH_PATH = Path("./scratch/publish")
# stubpacker.TEMPLATE_PATH = Path("./tests/publish/data/template")
# stubpacker.STUB_PATH = Path("./all-stubs")


@contextmanager
def cwd(path: Path):
    oldpwd = os.getcwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(oldpwd)


# test generation of different package names
@pytest.mark.parametrize(
    "family, pkg, port, board, expected",
    [
        ("micropython", COMBO_STUBS, "esp32", "GENERIC", "micropython-esp32-stubs"),
        ("micropython", COMBO_STUBS, "esp32", "TINY", "micropython-esp32-tiny-stubs"),
        ("micropython", DOC_STUBS, "esp32", None, "micropython-doc-stubs"),
        ("micropython", DOC_STUBS, "esp32", "GENERIC", "micropython-doc-stubs"),
        ("micropython", CORE_STUBS, None, None, "micropython-core-stubs"),
        ("micropython", CORE_STUBS, None, None, "micropython-core-stubs"),
        ("pycom", CORE_STUBS, None, None, "pycom-core-stubs"),
    ],
)
def test_package_name(family, pkg, port, board, expected):
    x = package_name(family=family, pkg_type=pkg, port=port, board=board)
    assert x == expected


# test get package from database
@pytest.mark.parametrize(
    "package_name, version, present",
    [
        ("micropython-esp32-stubs", "1.18", True),
        ("micropython-stm32-stubs", "1.17", True),
        # ("micropython-doc-stubs", "1.18", True),
        ("micropython-doc-stubs", "1.10", False),
        ("pycopy-foo-stubs", "1.18", False),
    ],
)
def test_get_package_info(pytestconfig, package_name, version, present):
    # Cache database in memory?
    # TODO: use test database with known content
    testdata = pytestconfig.rootpath / "tests/publish/data"
    db = get_database(testdata, production=False)
    pkg_info = get_package_info(db, Path("foo"), pkg_name=package_name, mpy_version=version)
    if present:
        assert pkg_info
        assert pkg_info["name"] == package_name
        assert pkg_info["mpy_version"] == version
        assert len(pkg_info["path"]) > 0
        assert len(pkg_info["pkg_version"]) > 0
        assert len(pkg_info["hash"]) > 0
        assert len(pkg_info["description"]) > 0
        assert len(pkg_info["stub_sources"]) > 0
    else:
        assert pkg_info == None


# test creating a DOC_STUBS package
@pytest.mark.parametrize(
    "pkg_type, port, board",
    [
        (DOC_STUBS, None, None),
        (COMBO_STUBS, "esp32", "GENERIC"),
    ],
)
# CORE_STUBS
def test_create_package(tmp_path, pytestconfig, pkg_type, port, board):
    """ "
    test Create a new package with the DOC_STUBS type
    - test the different methods to manipulate the package on disk
    """
    # allow stubpacker to use the test templates
    stubpacker.TEMPLATE_PATH = pytestconfig.rootpath / "tests/publish/data/template"

    # test data
    source = pytestconfig.rootpath / "tests/publish/data"
    root_path = tmp_path
    dest = root_path / "publish"
    shutil.copytree(source, dest)

    # TODO: need to endure that the stubs are avaialble in GHA testing
    stubpacker.ROOT_PATH = root_path
    stubpacker.STUB_PATH = pytestconfig.rootpath
    # stubpacker.PUBLISH_PATH = publish_path
    # stubpacker.TEMPLATE_PATH = pytestconfig.rootpath / "tests/publish/data/template"

    mpy_version = "v1.18"
    family = "micropython"
    pkg_name = f"foobar-{pkg_type}-stubs"

    package = create_package(
        pkg_name,
        mpy_version=mpy_version,
        family=family,
        port=port,
        board=board,
        pkg_type=pkg_type,
        stub_source="./all-stubs",  # for debugging
    )
    assert isinstance(package, stubpacker.StubPackage)
    run_common_package_tests(package, pkg_name, root_path, pkg_type)


def run_common_package_tests(package, pkg_name, root_path: Path, pkg_type):
    "a series of tests to re-use for all packages"
    assert isinstance(package, stubpacker.StubPackage)
    assert package.package_name == pkg_name

    assert not package.package_path.is_absolute(), "package path must be relative to publish folder"
    assert package.package_path.parent.name == "publish"
    assert (root_path / package.package_path).exists()

    assert len(package.stub_sources) >= 1
    for s in package.stub_sources:
        assert s[1].is_dir(), "stub source should be folder"
        assert s[1].exists(), "stubs source should exists"
        assert not s[1].is_absolute(), "should be a relative path"
    assert (root_path / package.package_path / "pyproject.toml").exists()
    # update existing pyproject.toml
    package.create_update_pyproject_toml()
    assert (root_path / package.package_path / "pyproject.toml").exists()

    package.create_readme()
    assert (root_path / package.package_path / "README.md").exists()
    package.create_license()
    assert (root_path / package.package_path / "LICENSE.md").exists()
    package.copy_stubs()
    filelist = list((root_path / package.package_path).rglob("*.py")) + list((root_path / package.package_path).rglob("*.pyi"))
    assert len(filelist) >= 1

    # do it all at once
    package.update_package_files()
    filelist = list((root_path / package.package_path).rglob("*.py")) + list((root_path / package.package_path).rglob("*.pyi"))
    assert len(filelist) >= 1

    package.update_included_stubs()
    stubs_in_pkg = package.pyproject["tool"]["poetry"]["packages"]  # type: ignore
    assert len(stubs_in_pkg) >= 1

    hash = package.create_hash()
    assert isinstance(hash, str)
    assert len(hash) > 30  # 41 bytes ?

    assert package.is_changed() == True

    result = package.check()
    assert result == True

    new_version = package.bump()
    assert new_version
    assert isinstance(new_version, stubpacker.Version)

    built = package.build()
    assert built
    assert (root_path / package.package_path / "dist").exists(), "Distribution folder should exist"
    filelist = list((root_path / package.package_path / "dist").glob("*.whl")) + list(
        (root_path / package.package_path / "dist").glob("*.tar.gz")
    )
    assert len(filelist) >= 2

    package.clean()
    filelist = list((root_path / package.package_path).rglob("*.py")) + list((root_path / package.package_path).rglob("*.pyi"))
    assert len(filelist) == 0


def test_package_from_json(tmp_path, pytestconfig):
    # test data
    source = pytestconfig.rootpath / "tests/publish/data"
    root_path = tmp_path
    publish_path = tmp_path / "publish"
    publish_path.mkdir(parents=True)

    # TODO: need to endure that the stubs are avaialble in GHA testing
    stubpacker.ROOT_PATH = tmp_path
    stubpacker.STUB_PATH = pytestconfig.rootpath
    # stubpacker.PUBLISH_PATH = publish_path
    # stubpacker.TEMPLATE_PATH = pytestconfig.rootpath / "tests/publish/data/template"

    mpy_version = "v1.18"
    family = "micropython"
    pkg_name = "foo-bar-stubs"
    # todo: include stubs in the test data
    # note uses `all-stubs` relative to the project as stub source
    json = {
        "name": "foo-bar-stubs",
        "mpy_version": "1.18",
        "publish": True,
        "pkg_version": "1.18.post6",
        "path": "publish/foo-v1_18-bar-stubs",
        "stub_sources": [
            ["Firmware stubs", "all-stubs/micropython-v1_17-stm32"],
            ["Frozen stubs", "all-stubs/micropython-v1_17-frozen/stm32/GENERIC"],
            ["Core Stubs", "all-stubs/cpython_core-pycopy"],
        ],
        "description": "foo bar stubs",
        "hash": "b09f9c819c9e98cbd9dfbc8158079146587e2d66",
    }

    package = stubpacker.StubPackage(pkg_name, version=mpy_version, json_data=json)
    assert isinstance(package, stubpacker.StubPackage)
    run_common_package_tests(package, pkg_name, root_path, pkg_type=None)
