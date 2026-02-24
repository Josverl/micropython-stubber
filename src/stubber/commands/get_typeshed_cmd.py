"""
get-typeshed  –  copy stdlib .pyi stubs from the bundled pyright/typeshed package.

When the ``--ai-enhance`` flag is provided the copied stubs are additionally
enriched with docstrings extracted from the running CPython interpreter so that
IDEs (e.g. Pylance/Pyright) can show documentation tooltips for MicroPython
stdlib-compatible modules.
"""

from pathlib import Path
from typing import Optional, Tuple

import rich_click as click
from mpflash.logger import log

from stubber.commands.cli import stubber_cli
from stubber.get_typeshed import MICROPYTHON_STDLIB_MODULES, get_typeshed_stubs
from stubber.utils.config import CONFIG
from stubber.utils.post import format_stubs


@stubber_cli.command(
    name="get-typeshed",
    aliases=["typeshed"],
)
@click.option(
    "--stub-path",
    "--stub-folder",
    "stub_path",
    default=None,
    type=click.Path(file_okay=False, dir_okay=True),
    help=("Destination folder for the extracted typeshed stubs. Defaults to <stub-path>/typeshed-stdlib."),
    show_default=True,
)
@click.option(
    "--module",
    "-m",
    "modules",
    multiple=True,
    default=[],
    help=("Module name(s) to copy. Can be specified multiple times. Defaults to all MicroPython-compatible stdlib modules."),
    show_default=False,
)
@click.option(
    "--ai-enhance/--no-ai-enhance",
    default=False,
    help=(
        "Inject CPython docstrings (from the running interpreter) into the "
        "copied stubs so IDEs can show documentation tooltips. "
        "Does NOT overwrite docstrings that are already present in the stub."
    ),
    show_default=True,
)
@click.option(
    "--format/--no-format",
    default=True,
    help="Run ruff formatter on the generated stubs.",
    show_default=True,
)
@click.option(
    "--list-modules",
    is_flag=True,
    default=False,
    help="List the default modules that will be copied and exit.",
)
def cli_get_typeshed(
    stub_path: Optional[str],
    modules: Tuple[str, ...],
    ai_enhance: bool,
    format: bool,
    list_modules: bool,
):
    """
    Copy stdlib .pyi stubs from the bundled pyright/typeshed package.

    This command extracts type-annotated stub files from the typeshed stdlib
    bundled inside the pyright pip package.  These stubs cover modules that
    exist in both CPython and MicroPython (e.g. ``json``, ``os``, ``sys``).

    Use ``--ai-enhance`` to additionally inject CPython docstrings from the
    running interpreter into the copied stubs, giving IDEs (Pylance/Pyright)
    richer documentation for MicroPython stdlib-compatible modules.

    MicroPython-specific docstrings are NEVER overwritten; docstrings are only
    added where they are not already present.
    """
    if list_modules:
        click.echo("Default MicroPython-compatible stdlib modules:")
        for mod in sorted(MICROPYTHON_STDLIB_MODULES):
            click.echo(f"  {mod}")
        return

    # Resolve destination path
    dest = Path(stub_path) if stub_path else (CONFIG.stub_path / "typeshed-stdlib")

    # Resolve module list
    module_list = list(modules) if modules else MICROPYTHON_STDLIB_MODULES

    log.info(
        f"Extracting typeshed stubs for {len(module_list)} module(s) "
        f"-> {dest}" + (" [ai-enhance: CPython docstrings will be injected]" if ai_enhance else "")
    )

    count, skipped = get_typeshed_stubs(
        dest_path=dest,
        modules=module_list,
        ai_enhance=ai_enhance,
    )

    if skipped:
        log.warning(f"Skipped {len(skipped)} module(s) not found in typeshed: {skipped}")

    log.info(f"Copied {count} module(s) to {dest}")

    if format and count:
        log.info("Formatting extracted stubs...")
        format_stubs(dest)

    log.info("Done.")
