import sys
from pathlib import Path
import subprocess
import pytest


@pytest.mark.parametrize("source", ["createstubs.py", "createstubs_mem.py", "createstubs_db.py"])
@pytest.mark.slow
def test_minification_py(tmp_path: Path, source: str):
    "python script - test creation of minified version"
    # load process.py in the same python environment
    source_path = Path("./board") / source
    # cmd = [sys.executable, "process.py", "minify", "--source", source_path.as_posix(), "--target", tmp_path.as_posix()]
    cmd = [sys.executable, "src/stubber/process.py", "minify", "--source", source_path.as_posix(), "--target", tmp_path.as_posix()]
    try:
        subproc = subprocess.run(cmd, timeout=100000)
        assert subproc.returncode == 0, "process minify should run without errors"

    except ImportError as e:
        print(e)
        pass
    # now test that log statements have been removed
    with open(tmp_path / source) as f:
        content = f.readlines()
    for line in content:
        assert line.find("._log") == -1, "all references to ._log have been removed"
