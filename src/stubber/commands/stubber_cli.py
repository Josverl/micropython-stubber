"""
command line interface - main group
"""
import click
import logging 

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

    # Set log level
    lvl = logging.WARNING
    if verbose:
        lvl = logging.INFO
    if debug:
        lvl = logging.DEBUG
    ctx.obj["loglevel"] = lvl

    logging.basicConfig(level=lvl)
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(lvl)