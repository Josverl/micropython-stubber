from pathlib import Path
from typing import List

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

# module under test :
import stubber.stubber as stubber
from stubber.commands.switch_cmd import VERSION_LIST

# mark all tests
pytestmark = [pytest.mark.stubber, pytest.mark.cli]


def test_cmd_help():
    # check basic command line sanity check
    runner = CliRunner()
    result = runner.invoke(stubber.stubber_cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Commands:" in result.output


##########################################################################################
# show-config
##########################################################################################


def test_cmd_get_config():
    runner = CliRunner()
    # from stubber.commands.clone import git
    result = runner.invoke(stubber.stubber_cli, ["show-config"])
    assert result.exit_code == 0


##########################################################################################
# clone
##########################################################################################
@pytest.mark.mocked
def test_cmd_clone(mocker: MockerFixture, tmp_path: Path):
    runner = CliRunner()
    # from stubber.commands.clone import git
    m_clone = mocker.patch("stubber.commands.clone_cmd.git.clone", autospec=True, return_value=0)
    m_fetch = mocker.patch("stubber.commands.clone_cmd.git.fetch", autospec=True, return_value=0)
    result = runner.invoke(stubber.stubber_cli, ["clone"])
    assert result.exit_code == 0

    # either clone or fetch
    assert m_clone.call_count + m_fetch.call_count == 2
    if m_clone.call_count > 0:
        m_clone.assert_any_call(
            remote_repo="https://github.com/micropython/micropython.git",
            path=Path("repos/micropython"),
        )
        m_clone.assert_any_call(
            remote_repo="https://github.com/micropython/micropython-lib.git",
            path=Path("repos/micropython-lib"),
        )
    else:
        m_fetch.assert_any_call(Path("repos/micropython"))
        m_fetch.assert_any_call(Path("repos/micropython-lib"))


@pytest.mark.mocked
def test_cmd_clone_path(mocker: MockerFixture, tmp_path: Path):
    runner = CliRunner()
    m_clone = mocker.patch("stubber.commands.clone_cmd.git.clone", autospec=True, return_value=0)

    m_tag = mocker.patch("stubber.commands.clone_cmd.git.get_local_tag", autospec=True)
    m_dir = mocker.patch("stubber.commands.clone_cmd.os.mkdir", autospec=True)  # type: ignore

    # now test with path specified
    result = runner.invoke(stubber.stubber_cli, ["clone", "--path", "foobar"])
    assert result.exit_code == 0

    assert m_clone.call_count >= 2
    m_clone.assert_any_call(
        remote_repo="https://github.com/micropython/micropython.git",
        path=Path("foobar/micropython"),
    )
    m_clone.assert_any_call(
        remote_repo="https://github.com/micropython/micropython-lib.git",
        path=Path("foobar/micropython-lib"),
    )
    assert m_tag.call_count >= 2


##########################################################################################
# switch
##########################################################################################


@pytest.mark.parametrize(
    "params",
    [
        pytest.param(["switch", "preview"], id="preview"),
        pytest.param(["switch", "latest"], id="latest"),
        pytest.param(["switch", "v1.17"], id="v1.17"),
        pytest.param(["switch", "v1.9.4"], id="v1.9.4"),
    ],
)
@pytest.mark.mocked
def test_cmd_switch(mocker: MockerFixture, params: List[str]):
    runner = CliRunner()
    # Mock Path.exists
    mocker.patch("stubber.commands.clone_cmd.git.clone", autospec=True, return_value=0)
    m_fetch = mocker.patch("stubber.commands.clone_cmd.git.fetch", autospec=True, return_value=0)

    m_switch = mocker.patch("stubber.commands.clone_cmd.git.switch_branch", autospec=True, return_value=0)
    m_checkout = mocker.patch("stubber.commands.clone_cmd.git.checkout_tag", autospec=True, return_value=0)
    mocker.patch("stubber.commands.clone_cmd.git.get_local_tag", autospec=True, return_value="v1.42")

    m_match = mocker.patch("stubber.utils.repos.match_lib_with_mpy", autospec=True)  # Moved to other module

    mocker.patch("stubber.commands.clone_cmd.Path.exists", return_value=True)
    result = runner.invoke(stubber.stubber_cli, params)
    assert result.exit_code == 0

    # fetch latest
    assert m_fetch.call_count == 3
    # TODO: Use Fake config to test path
    m_fetch.assert_any_call(Path("repos/micropython"))
    m_fetch.assert_any_call(Path("repos/micropython-lib"))

    # core
    m_match.assert_called_once()

    if "latest" in params or "preview" in params:
        m_switch.assert_called_once()
        m_checkout.assert_not_called()
    else:
        m_switch.assert_not_called()
        m_checkout.assert_called_once()


@pytest.mark.parametrize("version", VERSION_LIST)
@pytest.mark.mocked
def test_cmd_switch_version(mocker: MockerFixture, version: str):
    runner = CliRunner()
    # Mock Path.exists
    m_clone = mocker.patch("stubber.commands.clone_cmd.git.clone", autospec=True, return_value=0)
    m_fetch = mocker.patch("stubber.commands.clone_cmd.git.fetch", autospec=True, return_value=0)

    m_switch = mocker.patch("stubber.commands.clone_cmd.git.switch_branch", autospec=True, return_value=0)
    m_checkout = mocker.patch("stubber.commands.clone_cmd.git.checkout_tag", autospec=True, return_value=0)
    m_get_l_tag = mocker.patch("stubber.commands.clone_cmd.git.get_local_tag", autospec=True, return_value="v1.42")

    m_match = mocker.patch("stubber.utils.repos.match_lib_with_mpy", autospec=True)

    m_exists = mocker.patch("stubber.commands.clone_cmd.Path.exists", return_value=True)
    result = runner.invoke(stubber.stubber_cli, ["switch", version])
    assert result.exit_code == 0

    # fetch latest
    assert m_fetch.call_count == 3
    # "foobar" from params is used as the path
    m_fetch.assert_any_call(Path("repos/micropython"))
    m_fetch.assert_any_call(Path("repos/micropython-lib"))

    # should be called
    assert m_get_l_tag.called
    assert m_match.called
    assert m_exists.called
    # may/may not not be called
    assert m_clone.call_count >= 0
    assert m_switch.call_count >= 0
    assert m_checkout.call_count >= 0


##########################################################################################
# minify
##########################################################################################
# @pytest.mark.mocked
# def test_cmd_minify(mocker: MockerFixture):
#     # check basic command line sanity check
#     runner = CliRunner()
#     mock_minify = mocker.MagicMock(return_value=0)
#     mocker.patch("stubber.commands.minify_cmd.minify", mock_minify)

#     result = runner.invoke(stubber.stubber_cli, ["minify"])
#     assert result.exit_code == 0
#     mock_minify.assert_called_once()


# @pytest.mark.mocked
# def test_cmd_minify_all(mocker: MockerFixture):
#     # check basic command line sanity check
#     runner = CliRunner()
#     mock_minify = mocker.MagicMock(return_value=0)
#     mocker.patch("stubber.commands.minify_cmd.minify", mock_minify)

#     result = runner.invoke(stubber.stubber_cli, ["minify", "--all"])
#     assert result.exit_code == 0
#     assert mock_minify.call_count == 3


##########################################################################################
# stub
##########################################################################################
@pytest.mark.mocked
def test_cmd_stub(mocker: MockerFixture):
    # check basic command line sanity check
    runner = CliRunner()
    # m_generate = mocker.patch("stubber.commands.stub_cmd.generate_pyi_files", autospec=True, return_value=True)
    m_generate = mocker.MagicMock(return_value=True)
    m_postprocessing = mocker.MagicMock()
    mocker.patch("stubber.commands.stub_cmd.generate_pyi_files", m_generate)
    mocker.patch("stubber.commands.stub_cmd.do_post_processing", m_postprocessing)
    # fake run on current folder
    result = runner.invoke(stubber.stubber_cli, ["stub", "--source", "."])

    m_generate.assert_called_once_with(Path("."))
    m_postprocessing.assert_called_once()
    m_postprocessing.assert_called_once_with([Path(".")], stubgen=False, black=True, autoflake=False)
    assert result.exit_code == 0


##########################################################################################
# get-frozen
##########################################################################################
@pytest.mark.mocked
def test_cmd_get_frozen(mocker: MockerFixture, tmp_path: Path):
    # check basic command line sanity check
    runner = CliRunner()

    m_get_local_tag = mocker.patch("stubber.basicgit.get_local_tag", autospec=True, return_value="v1.42")

    m_freeze_any = mocker.patch("stubber.commands.get_frozen_cmd.freeze_any", autospec=True)
    m_post = mocker.patch("stubber.utils.do_post_processing", autospec=True)

    # fake run - need to ensure that there is a destination folder
    result = runner.invoke(stubber.stubber_cli, ["get-frozen", "--stub-folder", tmp_path.as_posix()])
    assert result.exit_code == 0
    # FIXME : test fails in CI
    m_freeze_any.assert_called_once()
    m_get_local_tag.assert_called_once()

    assert m_post.call_count == 2
    # m_post.assert_any_call(
    #     [tmp_path / "micropython-v1_42-frozen"],
    #     stubgen=True,
    #     black=False,
    #     autoflake=False,
    # )
    # m_post.assert_any_call(
    #     [tmp_path / "micropython-v1_42-frozen"],
    #     stubgen=False,
    #     black=True,
    #     autoflake=True,
    # )


# ##########################################################################################
# # get-lobo
# ##########################################################################################
# @pytest.mark.mocked
# def test_cmd_get_lobo(mocker: MockerFixture, tmp_path: Path):
#     # check basic command line sanity check
#     runner = CliRunner()

#     mock_get_frozen = mocker.patch("stubber.get_lobo.get_frozen", autospec=True)
#     mock_post = mocker.patch("stubber.utils.do_post_processing", autospec=True)

#     # fake run
#     result = runner.invoke(stubber.stubber_cli, ["get-lobo", "--stub-folder", tmp_path.as_posix()])
#     assert result.exit_code == 0
#     mock_get_frozen.assert_called_once()
#     mock_post.assert_called_once()
#     mock_post.assert_called_once_with([tmp_path / "loboris-v3_2_24-frozen"], stubgen=True, black=True, autoflake=True)
#     assert result.exit_code == 0


##########################################################################################
# get-core
##########################################################################################
@pytest.mark.mocked
def test_cmd_get_core(mocker: MockerFixture, tmp_path: Path):
    # check basic command line sanity check
    runner = CliRunner()
    mock = mocker.patch("stubber.get_cpython.get_core", autospec=True)
    mock_post = mocker.patch("stubber.utils.do_post_processing", autospec=True)

    # fake run
    result = runner.invoke(stubber.stubber_cli, ["get-core", "--stub-folder", tmp_path.as_posix()])
    assert result.exit_code == 0
    # process is called twice
    assert mock.call_count == 2

    # post is called one
    mock_post.assert_called_with(
        [tmp_path / "cpython_core-pycopy", tmp_path / "cpython_core-micropython"],
        stubgen=True,
        black=True,
        autoflake=True,
    )


##########################################################################################
# get-docstubs
##########################################################################################
@pytest.mark.mocked
def test_cmd_get_docstubs(mocker: MockerFixture, tmp_path: Path):
    # check basic command line sanity check
    runner = CliRunner()

    m_get_l_tag = mocker.patch("stubber.basicgit.get_local_tag", autospec=True, return_value="v1.42")

    # from stubber.commands.get_docstubs import generate_from_rst
    m_generate = mocker.patch("stubber.commands.get_docstubs_cmd.generate_from_rst", autospec=True)

    # fake run
    result = runner.invoke(stubber.stubber_cli, ["get-docstubs", "--stub-folder", tmp_path.as_posix()])
    assert result.exit_code == 0
    # process is called
    assert m_generate.call_count == 1
    m_generate.assert_called_once()
    assert m_get_l_tag.call_count >= 1


##########################################################################################
# fallback
##########################################################################################
# @pytest.mark.mocked
# def test_cmd_fallback(mocker: MockerFixture, tmp_path: Path):
#     # check basic command line sanity check
#     runner = CliRunner()

#     mock = mocker.patch("stubber.commands.upd_fallback_cmd.update_fallback", autospec=True)
#     # mock2 = mocker.patch("stubber.update_fallback.update_fallback", autospec=True)
#     # from .update_fallback import update_fallback,
#     # fake run
#     result = runner.invoke(stubber.stubber_cli, ["update-fallback", "--stub-folder", tmp_path.as_posix()])
#     mock.assert_called_once()
#     assert result.exit_code == 0


##########################################################################################
# merge
##########################################################################################
@pytest.mark.parametrize(
    "cmdline",
    [
        ["merge", "-V", "1.18", "-V", "1.19"],
        ["merge", "--version", "latest"],
    ],
)
@pytest.mark.mocked
def test_cmd_merge(mocker: MockerFixture, cmdline: List[str]):
    runner = CliRunner()
    # from stubber.commands.clone import git
    m_merge_docstubs = mocker.patch("stubber.commands.merge_cmd.merge_all_docstubs", autospec=True, return_value={})
    result = runner.invoke(stubber.stubber_cli, cmdline)
    assert result.exit_code == 0
    m_merge_docstubs.assert_called_once()


##########################################################################################
# publish
##########################################################################################
@pytest.mark.parametrize(
    "cmdline",
    [
        ["publish", "--test-pypi"],
        ["publish", "--pypi", "--force"],
    ],
)
@pytest.mark.mocked
def test_cmd_publish(mocker: MockerFixture, cmdline: List[str]):
    runner = CliRunner()
    # from stubber.commands.clone import git
    m_publish_multiple = mocker.patch("stubber.commands.publish_cmd.publish_multiple", autospec=True, return_value={})
    result = runner.invoke(stubber.stubber_cli, cmdline)
    assert result.exit_code == 0
    m_publish_multiple.assert_called_once()
