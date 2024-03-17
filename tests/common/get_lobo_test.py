import pytest
pytestmark = [pytest.mark.stubber,pytest.mark.legacy]

# Module Under Test
import stubber.get_lobo as get_lobo

# No Mocks, does actual download from github


def test_get_lobo(tmp_path):
    get_lobo.get_frozen(tmp_path)
    filecount = len(list(tmp_path.iterdir()))
    assert filecount == 15 + 1, "there should be 15 files + 1 manifest"
