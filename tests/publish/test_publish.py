from pathlib import Path

import pytest
from mock import MagicMock
from pytest_mock import MockerFixture
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


def test_publish_multiple(mocker):
    """Test publish_multiple"""
    from stubber.publish.publish import StubPackage

    m_build: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.build", autospec=True, return_value=True)
    m_publish: MagicMock = mocker.patch("stubber.publish.publish.StubPackage.publish", autospec=True, return_value=True)

    result = publish_multiple(production=False, frozen=True, dryrun=True)
    result = publish_multiple(production=False, frozen=True, dryrun=False)
    # TODO: add return and tests
    # #assert result != None , "Publish failed"
