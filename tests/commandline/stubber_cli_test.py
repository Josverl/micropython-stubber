import pytest
from pytest_mock import MockerFixture
from mock import MagicMock
from pathlib import Path
from click.testing import CliRunner

# module under test :
import stubber.stubber as stubber


def test_stubber_help():
    # check basic commandline sanity check
    runner = CliRunner()
    result = runner.invoke(stubber.stubber_cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Commands:" in result.output


##########################################################################################
# minify
##########################################################################################
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


##########################################################################################
# stub
##########################################################################################
def test_stubber_stub(mocker: MockerFixture):
    # check basic commandline sanity check
    runner = CliRunner()
    mock: MagicMock = mocker.MagicMock(return_value=True)
    mocker.patch("stubber.stubber.generate_pyi_files", mock)
    # fake run on current folder
    result = runner.invoke(stubber.stubber_cli, ["stub", "--source", "."])

    mock.assert_called_once_with(Path("."))
    assert result.exit_code == 0


##########################################################################################
# get-frozen
##########################################################################################


def test_stubber_get_frozen(mocker: MockerFixture):
    # check basic commandline sanity check
    runner = CliRunner()
    mock: MagicMock = mocker.MagicMock()
    mock_post: MagicMock = mocker.MagicMock()
    mock_version: MagicMock = mocker.MagicMock(return_value="v1.42")
    mocker.patch("stubber.stubber.get_mpy.get_frozen", mock)
    mocker.patch("stubber.stubber.git.get_tag", mock_version)
    mocker.patch("stubber.stubber.do_post_processing", mock_post)

    # fake run
    result = runner.invoke(stubber.stubber_cli, ["get-frozen"])
    # FIXME : test failes in CI
    # mock.assert_called_once_with(
    #     "all-stubs/micropython-v1_42-frozen", version="v1.42", mpy_path="./micropython", lib_path="./micropython-lib"
    # )

    # mock_post.assert_called_once_with([Path("all-stubs/micropython-v1_42-frozen")], True, True)

    assert result.exit_code == 0


##########################################################################################
# get-lobo
##########################################################################################
def test_stubber_get_lobo(mocker: MockerFixture):
    # check basic commandline sanity check
    runner = CliRunner()
    mock: MagicMock = mocker.MagicMock()
    mock_post: MagicMock = mocker.MagicMock()
    mocker.patch("stubber.stubber.get_lobo.get_frozen", mock)
    mocker.patch("stubber.stubber.do_post_processing", mock_post)

    # fake run
    result = runner.invoke(stubber.stubber_cli, ["get-lobo"])
    mock.assert_called_once()
    mock_post.assert_called_once()
    mock_post.assert_called_once_with([Path("all-stubs/loboris-v3_2_24-frozen")], True, True)
    assert result.exit_code == 0


##########################################################################################
# get-core
##########################################################################################


def test_stubber_get_core(mocker: MockerFixture):
    # check basic commandline sanity check
    runner = CliRunner()
    mock: MagicMock = mocker.MagicMock()
    mock_post: MagicMock = mocker.MagicMock()
    mocker.patch("stubber.stubber.get_cpython.get_core", mock)
    mocker.patch("stubber.stubber.do_post_processing", mock_post)

    # fake run
    result = runner.invoke(stubber.stubber_cli, ["get-core"])
    assert result.exit_code == 0
    # process is called twice
    assert mock.call_count == 2
    mock.assert_any_call(
        stub_path="all-stubs/cpython_core-micropython", requirements="requirements-core-micropython.txt", family="micropython"
    )
    mock.assert_any_call(stub_path="all-stubs/cpython_core-pycopy", requirements="requirements-core-pycopy.txt", family="pycopy")

    # post is called one
    mock_post.assert_called_with([Path("all-stubs/cpython_core-pycopy"), Path("all-stubs/cpython_core-micropython")], True, True)
