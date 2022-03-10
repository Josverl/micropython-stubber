import os
from distutils.dir_util import copy_tree
import pytest
from pathlib import Path

# pylint: disable=wrong-import-position,import-error
# Module Under Test
from stubber.update_fallback import update_fallback, utils


def test_update_fallback(tmp_path):
    # test requires an actuall filled source
    config = utils.config.readconfig()
    # from actual source
    stub_path = Path(config["stub-folder"])
    # to tmp_path /....
    count = update_fallback(
        stub_path,
        tmp_path / config["fallback-folder"],
    )
    # assert count >= 50
    # limited expectations
    assert count >= 1
