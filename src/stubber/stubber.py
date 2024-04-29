#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create, Process, and Maintain stubs ✏️  for MicroPython"""


from stubber.commands.build_cmd import cli_build
from stubber.commands.cli import stubber_cli
from stubber.commands.clone_cmd import cli_clone
from stubber.commands.config_cmd import cli_config
from stubber.commands.enrich_folder_cmd import cli_enrich_folder
from stubber.commands.get_core_cmd import cli_get_core
from stubber.commands.get_docstubs_cmd import cli_docstubs
from stubber.commands.get_frozen_cmd import cli_get_frozen
from stubber.commands.merge_cmd import cli_merge_docstubs
from stubber.commands.publish_cmd import cli_publish
from stubber.commands.stub_cmd import cli_stub
from stubber.commands.switch_cmd import cli_switch
from stubber.commands.variants_cmd import cli_variants
from stubber.commands.get_mcu_cmd import cli_create_mcu_stubs

##########################################################################################
if __name__ == "__main__":
    # add all commands to the CLI
    stubber_cli.add_command(cli_build)
    stubber_cli.add_command(cli_config)
    stubber_cli.add_command(cli_clone)
    stubber_cli.add_command(cli_switch)
    stubber_cli.add_command(cli_docstubs)
    stubber_cli.add_command(cli_get_core)
    stubber_cli.add_command(cli_get_frozen)
    stubber_cli.add_command(cli_stub)
    stubber_cli.add_command(cli_enrich_folder)
    stubber_cli.add_command(cli_publish)
    stubber_cli.add_command(cli_merge_docstubs)
    stubber_cli.add_command(cli_variants)
    stubber_cli.add_command(cli_create_mcu_stubs)
    stubber_cli()
