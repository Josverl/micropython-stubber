import pytest

from stubber.commands.publish_cmd import cli_publish



def test_cli_publish():
    cli_publish(family="micropython", version="1.18.0", port="esp32", board="GENERIC", production=False, dryrun=True, force=False)
