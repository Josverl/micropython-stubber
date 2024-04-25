from pathlib import Path
from typing import List

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

# module under test :
import mpflash.cli_group as cli_group
import mpflash.cli_main as cli_main

# mark all tests
pytestmark = [pytest.mark.mpflash, pytest.mark.cli]


##########################################################################################
# --help


def test_mpflash_help():
    # check basic command line sanity check
    runner = CliRunner()
    result = runner.invoke(cli_main.cli, ["--help"])
    assert result.exit_code == 0
    expected = ["Usage:", "Options", "Commands", "download", "flash", "list"]
    for word in expected:
        assert word in result.output


# def test_cli_verbose():
#     # can turn on verbose mode
#     runner = CliRunner()
#     result = runner.invoke(cli_main.cli, ["--verbose"])
#     assert cli_group.config.verbose == True


def test_cli_ignore():
    # can turn on verbose mode
    runner = CliRunner()
    result = runner.invoke(cli_main.cli, ["--ignore", "COM1", "--ignore", "COM2"])
    assert cli_group.config.ignore_ports == ["COM1", "COM2"]


@pytest.mark.parametrize(
    "params",
    [
        ["-q"],
        ["--quiet"],
        ["-q", "--verbose"],
        ["--quiet", "--verbose"],
    ],
)
def test_cli_quiet(params: List[str]):
    # can turn on verbose mode
    runner = CliRunner()
    result = runner.invoke(cli_main.cli, params)
    assert cli_group.config.quiet == True
    assert cli_group.config.verbose == False
