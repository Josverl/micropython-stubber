import sys
from pathlib import Path
import subprocess
import pytest

import stubber.minify as minify


@pytest.mark.parametrize("source", ["createstubs.py", "createstubs_mem.py", "createstubs_db.py"])
@pytest.mark.slow
def test_minification_py(tmp_path: Path, source: str):
    "python script - test creation of minified version"
    # load process.py in the same python environment
    source_path = Path("./board") / source

    result = minify.minify(source=source_path, target=tmp_path)
    assert result == 0
    # now test that log statements have been removed
    with open(tmp_path / source) as f:
        content = f.readlines()
    for line in content:
        assert line.find("._log") == -1, "all references to ._log have been removed"
