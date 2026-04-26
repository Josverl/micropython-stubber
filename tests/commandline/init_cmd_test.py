from pathlib import Path

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

import stubber.stubber as stubber

pytestmark = [pytest.mark.stubber, pytest.mark.cli, pytest.mark.mocked]


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def init_base_path(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def init_args(init_base_path: Path) -> list[str]:
    return ["init", "--path", init_base_path.as_posix()]


@pytest.fixture
def mock_chdir(mocker: MockerFixture):
    return mocker.patch("stubber.commands.init_cmd.os.chdir", autospec=True)


@pytest.fixture
def mock_git_clone(mocker: MockerFixture):
    return mocker.patch("stubber.commands.init_cmd.git.clone", autospec=True, return_value=0)


@pytest.fixture
def mock_clone_main(mocker: MockerFixture):
    return mocker.patch("stubber.commands.init_cmd.cli_clone.main", autospec=True, return_value=0)


@pytest.fixture
def mock_repo_paths(mocker: MockerFixture, tmp_path: Path):
    mpy = tmp_path / "repos" / "micropython"
    lib = tmp_path / "repos" / "micropython-lib"
    return mocker.patch("stubber.commands.init_cmd.repo_paths", autospec=True, return_value=(mpy, lib))


@pytest.fixture
def mock_fetch_repos(mocker: MockerFixture):
    # fetch_repos returns True on success
    return mocker.patch("stubber.commands.init_cmd.fetch_repos", autospec=True, return_value=True)


def test_cmd_init_existing_target(mocker: MockerFixture, runner: CliRunner, init_base_path: Path, init_args: list[str]):
    (init_base_path / "micropython-stubs").mkdir()

    m_git_clone = mocker.patch("stubber.commands.init_cmd.git.clone", autospec=True)
    m_clone_main = mocker.patch("stubber.commands.init_cmd.cli_clone.main", autospec=True)
    m_fetch_repos = mocker.patch("stubber.commands.init_cmd.fetch_repos", autospec=True)

    result = runner.invoke(stubber.stubber_cli, init_args)

    assert result.exit_code == 0
    m_git_clone.assert_not_called()
    m_clone_main.assert_not_called()
    m_fetch_repos.assert_not_called()


def test_cmd_init_success(
    runner: CliRunner,
    init_base_path: Path,
    init_args: list[str],
    mock_chdir,
    mock_git_clone,
    mock_clone_main,
    mock_repo_paths,
    mock_fetch_repos,
):
    result = runner.invoke(stubber.stubber_cli, init_args)

    assert result.exit_code == 0
    mock_git_clone.assert_called_once_with(
        remote_repo="https://github.com/josverl/micropython-stubs.git",
        path=init_base_path / "micropython-stubs",
    )
    mock_clone_main.assert_called_once_with(args=["--path", "repos"], standalone_mode=False)
    mock_repo_paths.assert_called_once_with(Path("repos"))
    mock_fetch_repos.assert_called_once()
    assert mock_fetch_repos.call_args.args[0] == "stable"
    # on success, cwd is changed once into stubs_path and NOT restored
    assert mock_chdir.call_count == 1


def test_cmd_init_stops_when_clone_step_fails(
    runner: CliRunner,
    init_args: list[str],
    mock_chdir,
    mock_git_clone,
    mock_fetch_repos,
    mocker: MockerFixture,
):
    m_clone_main = mocker.patch("stubber.commands.init_cmd.cli_clone.main", autospec=True, return_value=-1)

    result = runner.invoke(stubber.stubber_cli, init_args)

    assert result.exit_code == 0
    m_clone_main.assert_called_once_with(args=["--path", "repos"], standalone_mode=False)
    mock_fetch_repos.assert_not_called()
    # cwd restored on failure: chdir in + chdir back = 2
    assert mock_chdir.call_count == 2


def test_cmd_init_stops_when_switch_fails(
    runner: CliRunner,
    init_args: list[str],
    mock_chdir,
    mock_git_clone,
    mock_clone_main,
    mock_repo_paths,
    mocker: MockerFixture,
):
    mocker.patch("stubber.commands.init_cmd.fetch_repos", autospec=True, return_value=False)

    result = runner.invoke(stubber.stubber_cli, init_args)

    assert result.exit_code == 0
    mock_clone_main.assert_called_once()
    # cwd restored on failure
    assert mock_chdir.call_count == 2
