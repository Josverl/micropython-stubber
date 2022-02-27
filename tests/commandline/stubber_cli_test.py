from typing import Union
import pytest
from pytest_mock import MockerFixture
from mock import MagicMock
from pathlib import Path, WindowsPath, PosixPath
from click.testing import CliRunner
import sys

# module under test :
import stubber.stubber as stubber



def test_stubber_help():
    # check basic commandline sanity check
    runner = CliRunner()
    result = runner.invoke(stubber.stubber_cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Commands:" in result.output


def test_stubber_minify(mocker: MockerFixture):
    # check basic commandline sanity check
    runner = CliRunner()
    mock_minify: MagicMock = mocker.MagicMock(return_value=0)
    mocker.patch("stubber.stubber.minify", mock_minify)

    result = runner.invoke(stubber.stubber_cli, ["minify"])
    assert result.exit_code == 0
    mock_minify.assert_called_once_with("board/createstubs.py", "./minified", True, False, False)


def test_stubber_minify_all(mocker: MockerFixture):
    # check basic commandline sanity check
    runner = CliRunner()
    mock_minify: MagicMock = mocker.MagicMock(return_value=0)
    mocker.patch("stubber.stubber.minify", mock_minify)

    result = runner.invoke(stubber.stubber_cli, ["minify", "--all"])
    assert result.exit_code == 0
    assert mock_minify.call_count == 3
    mock_minify.assert_any_call("board/createstubs.py", "./minified", True, False, False)
    mock_minify.assert_any_call("board/createstubs_db.py", "./minified", True, False, False)
    mock_minify.assert_any_call("board/createstubs_mem.py", "./minified", True, False, False)


def test_stubber_stub(mocker: MockerFixture):
    # check basic commandline sanity check
    runner = CliRunner()
    mock: MagicMock = mocker.MagicMock(return_value=True)
    mocker.patch("stubber.stubber.generate_pyi_files", mock)

    # fake run on current folder
    result = runner.invoke(stubber.stubber_cli, ["stub", "--source", "."])

    if sys.platform.startswith("win"):
        mock.assert_called_once_with(WindowsPath("."))
    else:
        mock.assert_called_once_with(PosixPath("."))

    assert result.exit_code == 0
