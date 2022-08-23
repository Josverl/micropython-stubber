import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from pickle import TRUE

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
    publish_stubs,
)

# use our test paths
stubpacker.PUBLISH_PATH = Path("./scratch/publish")
stubpacker.TEMPLATE_PATH = Path("./tests/publish/data/template")
stubpacker.STUB_PATH = Path("./all-stubs")


@pytest.mark.parametrize(
    "pkg_type, ports, boards, versions",
    [
        (COMBO_STUBS, ["esp32"], ["GENERIC"], ["1.18"]),
        (DOC_STUBS, [], [], ["1.18"]),
    ],
)
def test_publish(
    pytestconfig,
    tmp_path,
    pkg_type,
    ports,
    boards,
    versions,
):
    source = pytestconfig.rootpath / "tests/publish/data"
    db = get_database(source, production=False)
    publish_path = tmp_path / "publish"
    publish_path.mkdir(parents=True)

    stubpacker.TEMPLATE_PATH = Path("./tests/publish/data/template")
    # TODO: need to endure that the stubs are avaialble in GHA testing
    stubpacker.ROOT_PATH = tmp_path
    stubpacker.STUB_PATH = pytestconfig.rootpath
    stubpacker.PUBLISH_PATH = publish_path

    # TODO: Mock publish 


    result = publish_stubs(
        versions=versions,
        ports=ports,
        boards=boards,
        db=db,
        pub_path=stubpacker.PUBLISH_PATH,
        pkg_type=pkg_type,
        family="micropython",
        production=False,  # Test-PyPi
        dryrun=False,  # don't publish , dont save to the database
        force=False,  # publish even if no changes
        clean=False,  # clean up afterards
    )
