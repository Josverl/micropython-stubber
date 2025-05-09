# sourcery skip: require-parameter-annotation, require-return-annotation
""" Test the package creation and manipulation"""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from stubber.publish.enums import StubSource
from stubber.publish.package import create_package, package_name
from stubber.publish.stubpackage import StubPackage

from .fakeconfig import FakeConfig

pytestmark = [pytest.mark.stubber]


# test generation of different package names
@pytest.mark.parametrize(
    "family, port, board, expected",
    [
        ("micropython", "esp32", "GENERIC", "micropython-esp32-stubs"),
        ("micropython", "esp32", "GENERIC_S3", "micropython-esp32-generic_s3-stubs"),
        ("micropython", "esp32", "generic", "micropython-esp32-stubs"),
        ("micropython", "esp32", "TINY", "micropython-esp32-tiny-stubs"),
        ("micropython", "esp32", "tiny", "micropython-esp32-tiny-stubs"),
    ],
)
def test_package_name(family, port, board, expected):
    x = package_name(family=family, port=port, board=board)
    assert x == expected


# test creating a package
# @pytest.mark.parametrize(
#     "version",
#     [
#         "v1.24.1",
#         # "v1.21.0",
#         # "v1.19.1",
#     ],
# )
@pytest.mark.parametrize(
    "version, port, board",
    [
        ("v1.24.1", "rp2", "RPI_PICO"),
        ("v1.24.1", "rp2", "RPI_PICOW"),
        # ("esp32", "GENERIC"),
        # ("esp32", "GENERIC_S3"),
        # ("esp32", "UM_TINYPICO"),
        # ("stm32", "PYBV1"),
        # ("esp32", "generic"),
    ],
)
# CORE_STUBS
def test_create_package(
    tmp_path, pytestconfig, version, port, board, mocker, monkeypatch: pytest.MonkeyPatch
):
    """ "
    test Create a new package with the DOC_STUBS type
    - test the different methods to manipulate the package on disk
    """
    publish_path = tmp_path / "publish"
    publish_path.mkdir(parents=True)

    stub_path = Path("./repos/micropython-stubs/stubs")
    template_path = pytestconfig.rootpath / "tests/publish/data/template"

    config = FakeConfig(
        publish_path=publish_path,
        stub_path=stub_path,
        template_path=template_path,
    )

    # # setup mock to configure the config
    # monkeypatch.setenv("MICROPYTHON-STUBBER_PUBLISH_PATH", publish_path.as_posix())
    # monkeypatch.setenv("MICROPYTHON-STUBBER_TEMPLATE_PATH", template_path.as_posix())
    # # resd config
    # TEST_CONFIG = readconfig(pytestconfig.rootpath / "tests/publish/data/config.yaml")
    # insert test config
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    family = "micropython"
    pkg_name = f"foobar-{port}-{board.lower()}-stubs"

    package = create_package(
        pkg_name,
        mpy_version=version,
        family=family,
        port=port,
        board=board,
        # stub_source="./all-stubs",  # for debugging
    )
    assert isinstance(package, StubPackage)
    run_common_package_tests(package, pkg_name, publish_path=publish_path, stub_path=stub_path)

    assert len(package.stub_sources) == 3, "new package must have 3 stub sources"

    all_found = False
    for s in package.stub_sources:
        if not (stub_path / s[1]).exists():
            all_found = False
            break

    if all_found:
        # some extra checks
        updated_sources = package.update_sources()
        assert updated_sources
        assert len(updated_sources) == 3, "new package must still have 3 stub sources"


read_db_data = [
    {
        "name": "foo-bar-stubs",
        "port": "foo",
        "board": "GENERIC",
        "variant": "",
        "mpy_version": "1.18",
        "publish": True,
        "pkg_version": "1.18.post6",
        "path": "foo-v1_18-bar-stubs",
        "stub_sources": """[
            ["MCU stubs", "micropython-v1_17-stm32"],
            ["Frozen stubs", "micropython-v1_17-frozen/stm32/GENERIC"],
            ["Core Stubs", "cpython_core-pycopy"]
        ]""",
        "description": "foo bar stubs",
        "hash": "b09f9c819c9e98cbd9dfbc8158079146587e2d66",
        "stub_hash": "",
    },
    {
        "name": "foo-bar-stubs",
        "port": "foo",
        "board": "bar",
        "variant": "",
        "mpy_version": "1.18",
        "publish": True,
        "pkg_version": "1.18.post6",
        "path": "foo-v1_18-bar-stubs",
        "stub_sources": """[
            ["MCU stubs", "stubs/micropython-v1_17-stm32"],
            ["Frozen stubs", "stubs/micropython-v1_17-frozen/stm32/GENERIC"],
            ["Core Stubs", "stubs/cpython_core-pycopy"]
        ]""",
        "description": "foo bar stubs",
        "hash": "b09f9c819c9e98cbd9dfbc8158079146587e2d66",
        "stub_hash": "",
    },
    {
        "name": "foo-bar-stubs",
        "port": "foo",
        "board": "bar",
        "variant": "ota",
        "mpy_version": "1.18",
        "publish": True,
        "pkg_version": "1.18.post6",
        "path": "publish/foo-v1_18-bar-stubs",
        "stub_sources": """[
            ["MCU stubs", "micropython-v1_17-stm32"]
        ]""",
        "description": "foo bar stubs",
        "hash": "b09f9c819c9e98cbd9dfbc8158079146587e2d66",
        "stub_hash": "1234567890",
    },
]


@pytest.mark.parametrize("json", read_db_data)
@pytest.mark.mocked
def test_package_from_json(tmp_path, pytestconfig, mocker: MockerFixture, json):
    # setup test configuration
    config = FakeConfig(tmp_path=tmp_path, rootpath=pytestconfig.rootpath)
    mocker.patch("stubber.publish.stubpackage.CONFIG", config)

    mpy_version = "v1.18"
    pkg_name = "foo-bar-stubs"
    port = "foo"
    board = "bar"
    # todo: include stubs in the test data
    # note uses `stubs` relative to the stubs_folder
    package = StubPackage(pkg_name, port, board=board, version=mpy_version, json_data=json)
    assert isinstance(package, StubPackage)
    run_common_package_tests(
        package,
        pkg_name,
        config.publish_path,
        stub_path=config.stub_path,
        test_build=False,
    )


def run_common_package_tests(
    package: StubPackage, pkg_name, publish_path: Path, stub_path: Path, test_build=True
):
    # sourcery skip: no-long-functions
    "a series of tests to re-use for all packages"
    assert isinstance(package, StubPackage)
    assert package.package_name == pkg_name
    # Package path
    assert package.package_path.relative_to(
        publish_path
    ), "package path should be relative to publish path"
    assert (package.package_path).exists()
    assert (package.package_path / "pyproject.toml").exists()
    # package path is all lowercase
    assert package.package_path.name == package.package_path.name.lower()

    assert len(package.stub_sources) >= 1

    # if stub_path.exists():
    #     for s in package.stub_sources:
    #         folder = stub_path / s[1]
    #         assert folder.is_dir(), "stub source should be folder"
    #         # assert folder.exists(), "stubs source should exists"
    #         assert not s[1].is_absolute(), "should be a relative path"

    # BOARD Name in frozen must be uppercase
    if src := [s for s in package.stub_sources if s[0] == StubSource.FROZEN]:
        board_name = src[0][1].name
        assert board_name == board_name.upper(), "BOARD Name in frozen must be uppercase"

    # update existing pyproject.toml
    package.create_update_pyproject_toml()
    assert (package.package_path / "pyproject.toml").exists()

    package.create_readme()
    assert (package.package_path / "README.md").exists()
    package.create_license()
    assert (package.package_path / "LICENSE.md").exists()

    new_version = package.bump()
    assert new_version
    assert isinstance(new_version, str)

    if not (stub_path.exists() and src and src[0][1].exists()):
        # withouth sources there is nothing to build
        return

    package.copy_stubs()
    filelist = list((package.package_path).rglob("*.py")) + list(
        (package.package_path).rglob("*.pyi")
    )
    assert len(filelist) >= 1

    # do it all at once
    package.update_package_files()
    filelist = list((package.package_path).rglob("*.py")) + list(
        (package.package_path).rglob("*.pyi")
    )
    assert len(filelist) >= 1

    package.update_pyproject_stubs()
    stubs_in_pkg = package.pyproject["tool"]["poetry"]["packages"]  # type: ignore
    assert len(stubs_in_pkg) >= 1

    packet_hash = package.calculate_hash()
    assert isinstance(packet_hash, str)
    assert len(packet_hash) > 30  # 41 bytes ?

    assert package.is_changed() == True

    result = package.check()
    assert result == True

    if test_build:
        built = package.poetry_build()
        assert built
        assert (package.package_path / "dist").exists(), "Distribution folder should exist"
        filelist = list((package.package_path / "dist").glob("*.whl")) + list(
            (package.package_path / "dist").glob("*.tar.gz")
        )
        assert len(filelist) >= 2

    package.clean()
    filelist = list((package.package_path).rglob("*.py")) + list(
        (package.package_path).rglob("*.pyi")
    )
    assert len(filelist) == 0
