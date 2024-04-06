import json

import rich_click as click
from rich import print

from .cli_group import cli
from .list import list_mcus, show_mcus
from .logger import make_quiet


@cli.command("list", help="List the connected MCU boards.")
@click.option(
    "--json",
    "-j",
    "as_json",
    is_flag=True,
    default=False,
    show_default=True,
    help="""Output in json format""",
)
@click.option(
    "--progress/--no-progress",
    "progress",
    is_flag=True,
    default=True,
    show_default=True,
    help="""Show progress""",
)
def cli_list_mcus(as_json: bool, progress: bool = True):
    """List the connected MCU boards, and output in a nice table or json."""
    if as_json:
        # avoid noise in json output
        make_quiet()

    conn_mcus = list_mcus()
    if as_json:
        print(json.dumps([mcu.__dict__ for mcu in conn_mcus], indent=4))
        progress = False
    if progress:
        show_mcus(conn_mcus, refresh=False)
    return conn_mcus
