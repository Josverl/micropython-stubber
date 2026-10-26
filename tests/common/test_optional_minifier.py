import subprocess
import sys
from importlib.metadata import requires

from packaging.requirements import Requirement


def test_minifier_is_not_a_runtime_dependency():
    dependencies = requires("micropython-stubber")
    assert dependencies is not None
    assert "python-minifier" not in {Requirement(dependency).name for dependency in dependencies}


def test_cli_without_minifier():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import sys
sys.modules["python_minifier"] = None
from click.testing import CliRunner
from stubber.stubber import stubber_cli
for args in (["--help"], ["make-variants", "--help"]):
    result = CliRunner().invoke(stubber_cli, args)
    assert result.exit_code == 0, result.output
""",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
