#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create, Process, and Maintain stubs ✏️  for MicroPython"""


from stubber.commands.cli import stubber_cli
from stubber.commands.clone_cmd import cli_clone
from stubber.commands.config_cmd import cli_config
from stubber.commands.enrich_folder_cmd import cli_enrich_folder
from stubber.commands.get_core_cmd import cli_get_core
from stubber.commands.get_docstubs_cmd import cli_docstubs
from stubber.commands.get_frozen_cmd import cli_get_frozen
from stubber.commands.get_lobo_cmd import cli_get_lobo
from stubber.commands.merge_cmd import cli_merge_docstubs
from stubber.commands.minify_cmd import cli_minify
from stubber.commands.publish_cmd import cli_publish
from stubber.commands.stub_cmd import cli_stub
from stubber.commands.switch_cmd import cli_switch
from stubber.commands.upd_fallback_cmd import cli_update_fallback
from stubber.commands.upd_module_list_cmd import cli_update_module_list

##########################################################################################
# log = logging.getLogger("stubber")
#########################################################################################


##########################################################################################

if __name__ == "__main__":
    # add all commands to the CLI
    stubber_cli.add_command(cli_config)
    stubber_cli.add_command(cli_clone)
    stubber_cli.add_command(cli_switch)
    stubber_cli.add_command(cli_docstubs)
    stubber_cli.add_command(cli_get_core)
    stubber_cli.add_command(cli_get_frozen)
    stubber_cli.add_command(cli_get_lobo)
    stubber_cli.add_command(cli_stub)
    stubber_cli.add_command(cli_enrich_folder)
    stubber_cli.add_command(cli_minify)
    stubber_cli.add_command(cli_publish)
    stubber_cli.add_command(cli_merge_docstubs)
    stubber_cli.add_command(cli_update_module_list)
    stubber_cli.add_command(cli_update_fallback)
    stubber_cli()
