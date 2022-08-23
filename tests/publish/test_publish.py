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
    publish_board_stubs,
)

# use our test paths
stubpacker.PUBLISH_PATH = Path("./scratch/publish")
stubpacker.TEMPLATE_PATH = Path("./tests/publish/data/template")
stubpacker.STUB_PATH = Path("./all-stubs")


def test_publish(pytestconfig):
    source = pytestconfig.rootpath / "tests/publish/data"
    db = get_database(source, production=False)

    result = publish_board_stubs(
        versions=["1.18", "1.17"],
        ports=["esp32", "stm32"],
        boards=["GENERIC", "TINY"],
        db=db,
        pub_path=stubpacker.PUBLISH_PATH,
        pkg_type=COMBO_STUBS,
        family="micropython",
        production=False,  # Test-PyPi
        dryrun=True,  # don't publish , dont save to the database
        force=False,  # publish even if no changes
        clean=False,  # clean up afterards
    )

    assert result == True
