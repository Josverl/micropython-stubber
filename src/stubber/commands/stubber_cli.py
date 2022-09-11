"""
command line interface - main group
"""
import sys

import click
from loguru import logger as log


@click.group(chain=True)
@click.version_option(package_name="micropython-stubber", prog_name="micropython-stubber✏️ ")
@click.option("--verbose", "-vv", is_flag=True, default=False)
@click.option("--debug", "-vvv", is_flag=True, default=False)

# TODO: add stubfolder to top level and pass using context
# @click.option("--stub-folder", "-stubs", default=config.stub_folder, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.pass_context
def stubber_cli(ctx, verbose=False, debug=False):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    ctx.ensure_object(dict)
    # replace std log handler with a custom one capped on INFO level
    log.remove()
    level = "DEBUG" if debug else "INFO" if verbose else "WARNING"
    log.add(sys.stderr, level=level, backtrace=True, diagnose=True)
    ctx.obj["loglevel"] = level
