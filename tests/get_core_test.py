from pathlib import Path
import pytest
from mock import MagicMock
from pytest_mock import MockerFixture

# Module Under Test
import stubber.get_cpython


# No Mocks, does actual extraction using pip-install
@pytest.mark.skip(reason="Does actual extraction using pip-install")
@pytest.mark.parametrize(
    "requirements",
    [
        "requirements-core-micropython.txt",
        "requirements-core-pycopy.txt",
    ],
)
@pytest.mark.slow
def test_get_cpython(requirements, tmp_path):
    stubber.get_cpython.get_core(requirements=requirements, stub_path=tmp_path)
    stubfiles = list(tmp_path.rglob("*.py"))
    assert len(stubfiles) > 1


################################################################
# Mocked
################################################################


@pytest.mark.parametrize(
    "requirements",
    [
        "requirements-core-micropython.txt",
        "requirements-core-pycopy.txt",
    ],
)
@pytest.mark.mocked
def test_get_cpython_mocked(
    requirements,
    tmp_path: Path,
    mocker: MockerFixture,
):
    """
    test create stubs with mocks to avoid actual download and extraction

    """
    m_os_makedirs: MagicMock = mocker.patch("stubber.get_cpython.os.makedirs", autospec=True)

    # mock subprocess run with a function that creates a single file in the destination
    def mock_subprocess_run(cmd, *args, **kwargs):
        tempfolder = cmd[3]
        # create a single file in the tempfolder
        (Path(tempfolder) / "testfile.py").touch()

    m_spr: MagicMock = mocker.patch("stubber.get_cpython.subprocess.run", autospec=True, side_effect=mock_subprocess_run)

    stubber.get_cpython.get_core(requirements=requirements, stub_path=tmp_path)
    assert m_os_makedirs.call_count >= 1
    assert m_spr.call_count >= 1
    stubfiles = list(tmp_path.rglob("*.py"))
    assert len(stubfiles) == 1
