from pathlib import Path

import pytest
from stubber.publish.database import get_database
import stubber.publish.stubpacker as stubpacker
from stubber.publish.publish_stubs import (
    ALL_TYPES,
    COMBO_STUBS,
    CORE_STUBS,
    DOC_STUBS,
    publish_combo_stubs,
    publish_doc_stubs,
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

    if pkg_type == COMBO_STUBS:
        result = publish_combo_stubs(
            pkg_type=pkg_type,
            family="micropython",
            ports=ports,
            boards=boards,
            versions=versions,
            db=db,
            pub_path=stubpacker.PUBLISH_PATH,
            production=False,  # Test-PyPi
            dryrun=False,  # don't publish , dont save to the database
            force=False,  # publish even if no changes
            clean=False,  # clean up afterards
        )
    elif pkg_type == DOC_STUBS:
        result = publish_doc_stubs(
            pkg_type=pkg_type,
            family="micropython",
            ports=ports,
            boards=boards,
            versions=versions,
            db=db,
            pub_path=stubpacker.PUBLISH_PATH,
            production=False,  # Test-PyPi
            dryrun=False,  # don't publish , dont save to the database
            force=False,  # publish even if no changes
            clean=False,  # clean up afterards
        )
