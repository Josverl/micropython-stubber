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
# clone
##########################################################################################
def test_stubber_clone(mocker: MockerFixture, tmp_path: Path):
    runner = CliRunner()
    mock_clone: MagicMock = mocker.MagicMock(return_value=0)
    mocker.patch("stubber.stubber.git.clone", mock_clone)
    result = runner.invoke(stubber.stubber_cli, ["clone"])
    assert result.exit_code == 0

    assert mock_clone.call_count >= 2
    mock_clone.assert_any_call(remote_repo="https://github.com/micropython/micropython.git", path=Path("repos/micropython"))
    mock_clone.assert_any_call(remote_repo="https://github.com/micropython/micropython-lib.git", path=Path("repos/micropython-lib"))

    mock_clone.reset_mock()
    # now test with path specified
    result = runner.invoke(stubber.stubber_cli, ["clone", "--path", "foobar"])
    assert result.exit_code == 0

    assert mock_clone.call_count >= 2
    mock_clone.assert_any_call(remote_repo="https://github.com/micropython/micropython.git", path=Path("foobar/micropython"))
    mock_clone.assert_any_call(remote_repo="https://github.com/micropython/micropython-lib.git", path=Path("foobar/micropython-lib"))


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
    # mock: MagicMock = mocker.MagicMock(return_value=True)
    mock: MagicMock = mocker.patch("stubber.stubber.utils.generate_pyi_files", autospec=True, return_value=True)
    # fake run on current folder
    result = runner.invoke(stubber.stubber_cli, ["stub", "--source", "."])

    mock.assert_called_once_with(Path("."))
    assert result.exit_code == 0


##########################################################################################
# get-frozen
##########################################################################################


def test_stubber_get_frozen(mocker: MockerFixture, tmp_path: Path):
    # check basic commandline sanity check
    runner = CliRunner()

    mock_version: MagicMock = mocker.patch("stubber.stubber.git.get_tag", autospec=True, return_value="v1.42")

    mock: MagicMock = mocker.patch("stubber.stubber.get_mpy.get_frozen", autospec=True)
    mock_post: MagicMock = mocker.patch("stubber.stubber.utils.do_post_processing", autospec=True)

    # fake run - need to ensure that there is a destination folder
    result = runner.invoke(stubber.stubber_cli, ["get-frozen", "--stub-folder", tmp_path.as_posix()])
    assert result.exit_code == 0
    # FIXME : test failes in CI
    mock.assert_called_once()
    mock_version.assert_called_once()

    mock_post.assert_called_once_with([tmp_path / "micropython-v1_42-frozen"], True, True)


##########################################################################################
# get-lobo
##########################################################################################
def test_stubber_get_lobo(mocker: MockerFixture, tmp_path: Path):
    # check basic commandline sanity check
    runner = CliRunner()

    mock: MagicMock = mocker.patch("stubber.stubber.get_lobo.get_frozen", autospec=True)
    mock_post: MagicMock = mocker.patch("stubber.stubber.utils.do_post_processing", autospec=True)

    # fake run
    result = runner.invoke(stubber.stubber_cli, ["get-lobo", "--stub-folder", tmp_path.as_posix()])
    mock.assert_called_once()
    mock_post.assert_called_once()
    mock_post.assert_called_once_with([tmp_path / "loboris-v3_2_24-frozen"], True, True)
    assert result.exit_code == 0


##########################################################################################
# get-core
##########################################################################################


def test_stubber_get_core(mocker: MockerFixture, tmp_path: Path):
    # check basic commandline sanity check
    runner = CliRunner()
    mock: MagicMock = mocker.patch("stubber.stubber.get_cpython.get_core", autospec=True)
    mock_post: MagicMock = mocker.patch("stubber.stubber.utils.do_post_processing", autospec=True)

    # fake run
    result = runner.invoke(stubber.stubber_cli, ["get-core", "--stub-folder", tmp_path.as_posix()])
    assert result.exit_code == 0
    # process is called twice
    assert mock.call_count == 2

    # post is called one
    mock_post.assert_called_with([tmp_path / "cpython_core-pycopy", tmp_path / "cpython_core-micropython"], True, True)


##########################################################################################
# get-docstubs
##########################################################################################


def test_stubber_get_docstubs(mocker: MockerFixture, tmp_path: Path):
    # check basic commandline sanity check
    runner = CliRunner()

    mock_version: MagicMock = mocker.patch("stubber.stubber.git.get_tag", autospec=True, return_value="v1.42")

    mock: MagicMock = mocker.patch("stubber.stubber.generate_from_rst", autospec=True)

    mock_post: MagicMock = mocker.patch("stubber.stubber.utils.do_post_processing", autospec=True)

    # fake run
    result = runner.invoke(stubber.stubber_cli, ["get-docstubs", "--stub-folder", tmp_path.as_posix()])
    assert result.exit_code == 0
    # process is called twice
    assert mock.call_count == 1
    mock.assert_called_once()
    assert mock_version.call_count >=1

    # post is called one
    mock_post.assert_called_with([tmp_path / "micropython-v1_42-docstubs"], False, True)
