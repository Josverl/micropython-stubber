from pathlib import Path

import pytest
from stubber.publish.database import get_database
from stubber.publish.publish_stubs import ALL_TYPES, COMBO_STUBS, CORE_STUBS, DOC_STUBS, publish_combo_stubs, publish_doc_stubs
from stubber.utils.config import CONFIG, readconfig

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
    mocker,
    pkg_type,
    ports,
    boards,
    versions,
):
    source = pytestconfig.rootpath / "tests/publish/data"
    db = get_database(source, production=False)

    source = pytestconfig.rootpath / "tests/publish/data"
    PUBLISH_PATH = tmp_path / "publish"
    PUBLISH_PATH.mkdir(parents=True)

    #  need to ensure that the stubs are avaialble in GHA testing
    STUB_PATH = Path("./repos/micropython-stubs/stubs")
    TEMPLATE_PATH = pytestconfig.rootpath / "tests/publish/data/template"

    mocker.patch("stubber.publish.stubpacker.STUB_PATH", STUB_PATH)
    mocker.patch("stubber.publish.stubpacker.TEMPLATE_PATH", TEMPLATE_PATH)
    mocker.patch("stubber.publish.stubpacker.PUBLISH_PATH", PUBLISH_PATH)

    if pkg_type == COMBO_STUBS:
        result = publish_combo_stubs(
            pkg_type=pkg_type,
            family="micropython",
            ports=ports,
            boards=boards,
            versions=versions,
            db=db,
            pub_path=PUBLISH_PATH,
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
            pub_path=PUBLISH_PATH,
            production=False,  # Test-PyPi
            dryrun=False,  # don't publish , dont save to the database
            force=False,  # publish even if no changes
            clean=False,  # clean up afterards
        )
