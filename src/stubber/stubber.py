#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create, Process, and Maintain stubs ✏️  for MicroPython"""


import logging

from stubber.commands.clone import cli_clone
from stubber.commands.enrich_folder import cli_enrich_folder
from stubber.commands.get_core import cli_get_core
from stubber.commands.get_docstubs import cli_docstubs
from stubber.commands.get_frozen import cli_get_frozen
from stubber.commands.get_lobo import cli_get_lobo
from stubber.commands.stub import cli_stub
from stubber.commands.stubber_cli import stubber_cli
from stubber.commands.switch import cli_switch
from stubber.commands.update_fallback import cli_update_fallback
from stubber.utils.my_version import __version__

##########################################################################################
log = logging.getLogger("stubber")
#########################################################################################


##########################################################################################

if __name__ == "__main__":
    # add all commands to the CLI
    stubber_cli.add_command(cli_clone)
    stubber_cli.add_command(cli_switch)
    stubber_cli.add_command(cli_docstubs)
    stubber_cli.add_command(cli_get_core)
    stubber_cli.add_command(cli_get_frozen)
    stubber_cli.add_command(cli_get_lobo)
    stubber_cli.add_command(cli_stub)
    stubber_cli.add_command(cli_update_fallback)
    stubber_cli.add_command(cli_enrich_folder)

    stubber_cli()
