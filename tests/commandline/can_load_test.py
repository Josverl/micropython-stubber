from pathlib import Path
from typing import List

import pytest
from click.testing import CliRunner
from mock import MagicMock
from pytest_mock import MockerFixture


def test_can_load():
    # can we import the base module?
    import stubber

    # can we import the cli
    import stubber.commands.stubber_cli


def test_can_load_commands():
    from stubber.commands.enrich_folder import cli_enrich_folder
