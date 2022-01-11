import pytest
import subprocess

def test_black_installed():
    "Check if black is installed and can be run"
    cmd = ["black", "--version"]
    result = subprocess.run(cmd, capture_output=True)
    assert "black" in result.stdout.decode("utf-8")
    # black does not use semver :-(


def test_pyright_installed():
    "Check if Pyright is installed and can be run"
    cmd = ["pyright", "--version"]
    result = subprocess.run(cmd, capture_output=True)
    assert "pyright" in result.stdout.decode("utf-8")
    ver = result.stdout.decode("utf-8").strip().split()[-1]
    assert version.parse(ver) > version.parse("1.1")


def test_mpy-cross_installed():
    "Check if mpy-cross can be installed and run"
    cmd = ["mpy-cross", "--version"]
    result = subprocess.run(cmd, capture_output=True)
    assert "mpy-cross emitting mpy v5" in result.stdout.decode("utf-8")

