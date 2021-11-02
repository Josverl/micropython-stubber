import sys
import subprocess


def test_minifier(tmp_path):
    "test creation of minified version"
    # load process.py in the same python environment
    # TODO: Use temp_path to generate stubs
    cmd = [sys.executable, "process.py", "minify"]
    try:
        subproc = subprocess.run(cmd, timeout=100000)
        assert subproc.returncode == 0, "process minify should run without errors"

    except ImportError as e:
        print(e)
        pass


def test_minified_no_log():
    with open("minified/createstubs.py") as f:
        content = f.readlines()
    for line in content:
        assert line.find("._log") == -1, "all references to ._log have been removed"
