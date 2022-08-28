from pathlib import Path

import pytest
from stubber.publish.database import get_database
from stubber.publish.package import (ALL_TYPES, COMBO_STUBS, CORE_STUBS,
                                     DOC_STUBS)
from stubber.publish.publish import publish, publish_multiple
from stubber.utils.config import CONFIG, readconfig

from .fakeconfig import FakeConfig

# @pytest.mark.parametrize(
#     "pkg_type, ports, boards, versions",
#     [
#         (COMBO_STUBS, ["esp32"], ["GENERIC"], ["1.18"]),
#         (DOC_STUBS, [], [], ["1.18"]),
#     ],
# )

def test_publish_multiple():
    result = publish_multiple(frozen=True)
    assert result != None


# def test_publish(
#     pytestconfig,
#     tmp_path,
#     mocker,
#     pkg_type,
#     ports,
#     boards,
#     versions,
# ):
#     source = pytestconfig.rootpath / "tests/publish/data"
#     db = get_database(source, production=False)

#     source = pytestconfig.rootpath / "tests/publish/data"
#     publish_path = tmp_path / "publish"
#     publish_path.mkdir(parents=True)

#     #  need to ensure that the stubs are avaialble in GHA testing
#     stub_path = Path("./repos/micropython-stubs/stubs")
#     template_path = pytestconfig.rootpath / "tests/publish/data/template"

#     config = FakeConfig(
#         publish_path=publish_path,
#         stub_path=stub_path,
#         template_path=template_path,
#     )

#     mocker.patch("stubber.publish.stubpacker.CONFIG", config)

#     if pkg_type == COMBO_STUBS:
#         result = publish_combo_stubs(
#             pkg_type=pkg_type,
#             family="micropython",
#             ports=ports,
#             boards=boards,
#             versions=versions,
#             db=db,
#             pub_path=publish_path,
#             production=False,  # Test-PyPi
#             dryrun=False,  # don't publish , dont save to the database
#             force=False,  # publish even if no changes
#             clean=False,  # clean up afterards
#         )
#     elif pkg_type == DOC_STUBS:
#         result = publish_doc_stubs(
#             pkg_type=pkg_type,
#             family="micropython",
#             ports=ports,
#             boards=boards,
#             versions=versions,
#             db=db,
#             pub_path=publish_path,
#             production=False,  # Test-PyPi
#             dryrun=False,  # don't publish , dont save to the database
#             force=False,  # publish even if no changes
#             clean=False,  # clean up afterards
#         )
