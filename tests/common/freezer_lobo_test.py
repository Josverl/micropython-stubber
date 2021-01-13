import os
import pytest

# pylint: disable=wrong-import-position,import-error
# Module Under Test
import get_lobo

# No Mocks, does actual download from github

def test_freezer_lobo(tmp_path):
    get_lobo.get_frozen(tmp_path)
    filecount = len(list(tmp_path.iterdir()))
    assert  filecount == 19, "there should be 18 files + 1 manifest"




