import subprocess

import pytest
from packaging import version

pytestmark = [pytest.mark.stubber]


@pytest.mark.parametrize(
    "tool_name, tool_version",
    [
        ("autoflake", "2.2.1"),
        ("black", "22.12.0"),
        ("pyright", "1.1"),
    ],
)
@pytest.mark.skip("Only needed to debug venv installation issues")
def test_tool_installed(tool_name, tool_version):
    "Check if a tool is installed and can be run"
    cmd = [tool_name, "--version"]
    result = subprocess.run(cmd, capture_output=True)
    out = result.stdout.decode("utf-8").strip()
    assert tool_name in out

    # Assume the last word is the version
    if tool_name == "black":
        # remove too much info
        out = out.split("(")[0]
    ver = out.split()[-1]
    if isinstance(version.parse(ver), version.Version):
        # avoid issues with non-standard versions and 'latest'
        assert version.parse(ver) >= version.parse(tool_version)


def test_mpy_cross_bytecode_version():
    "Check if mpy-cross can be installed and run"
    cmd = ["pipx", "run", "mpy-cross", "--version"]
    result = subprocess.run(cmd, capture_output=True)
    assert "mpy-cross emitting mpy" in result.stdout.decode("utf-8")
    # assert "mpy-cross emitting mpy v5" in result.stdout.decode("utf-8")
