from typing import List

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

# # module under test :
from mpflash import cli_main

# mark all tests
pytestmark = pytest.mark.mpflash


##########################################################################################
# list


@pytest.mark.parametrize(
    "id, ex_code, args",
    [
        ("1", 0, ["list"]),
        ("2", 0, ["list", "--json"]),
        ("3", 0, ["list", "--no-progress"]),
        ("4", 0, ["list", "--json", "--no-progress"]),
    ],
)
def test_mpflash_list(id, ex_code, args: List[str], mocker: MockerFixture):

    m_list_mcus = mocker.patch("mpflash.cli_list.list_mcus", return_value=[], autospec=True)
    m_show_mcus = mocker.patch("mpflash.cli_list.show_mcus", return_value=None, autospec=True)
    m_print = mocker.patch("mpflash.cli_list.print", return_value=None, autospec=True)

    runner = CliRunner()
    result = runner.invoke(cli_main.cli, args)
    assert result.exit_code == ex_code

    m_list_mcus.assert_called_once()
    if "--json" in args:
        m_print.assert_called_once()
    if "--no-progress" not in args and "--json" not in args:
        m_show_mcus.assert_called_once()
