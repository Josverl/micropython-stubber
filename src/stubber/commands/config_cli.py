##########################################################################################
# clone
##########################################################################################
import logging
import os
from pathlib import Path

import click
from stubber.utils.config import CONFIG
from stubber.utils.my_version import __version__

from .stubber_cli import stubber_cli

##########################################################################################
log = logging.getLogger("stubber")
#########################################################################################


@stubber_cli.command(name="show-config")
def cli_config():
    """
    Show the current configuration
    """

    click.echo(f"CONFIG.repo_path           {CONFIG.repo_path}")
    click.echo(f"CONFIG.mpy_path            {CONFIG.mpy_path}")
    click.echo(f"CONFIG.mpy_lib_path        {CONFIG.mpy_lib_path}")

    click.echo(f"CONFIG.stub_path           {CONFIG.stub_path}")
    click.echo(f"CONFIG.publish_path        {CONFIG.publish_path}")
    click.echo(f"CONFIG.template_path       {CONFIG.template_path}")
