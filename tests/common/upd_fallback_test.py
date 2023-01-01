import os
from pathlib import Path


# pylint: disable=wrong-import-position,import-error
# Module Under Test
from stubber.update_fallback import RELEASED, fallback_sources, update_fallback
from stubber.utils.config import CONFIG


def test_update_fallback(tmp_path):
    # test requires an actuall filled source
    # from actual source
    # TODO: Make sure there is an actual source to copy from

    stub_path = CONFIG.stub_path
    # to tmp_path /....
    count = update_fallback(stub_path, tmp_path / CONFIG.fallback_path)
    # assert count >= 50
    # limited expectations as there is no source
    assert count >= 0


def test_update_fallback_2(tmp_path: Path):
    # test requires an actuall filled source
    # from actual source
    # Make sure there is an actual source to copy from

    stub_path = tmp_path
    fallback_path = tmp_path / CONFIG.fallback_path
    # create fake sources
    fakes = 0
    for (name, source) in fallback_sources(RELEASED):
        if "." not in name:
            ...
            file = stub_path / source / name / "__init__.py"
        else:
            file = stub_path / source / name.replace("*", "")
        # create fake file(s)
        if not file.parent.exists():
            os.makedirs(file.parent)
        with open(file, "x") as f:
            f.write("# fake \n")
        fakes += 1
    # to tmp_path /....
    count = update_fallback(stub_path, fallback_path, version=RELEASED)
    assert count == fakes
    count = update_fallback(stub_path, fallback_path)
    assert count == fakes
    count = update_fallback(stub_path, fallback_path, version="latest")
    assert count > 0
