"""Create or update .pyi type hint files."""

##########################################################################################
# stub
##########################################################################################

from mpflash.logger import log
from pathlib import Path
from typing import Union

import rich_click as click
from stubber.utils import generate_pyi_files
from stubber.utils.post import do_post_processing

from .cli import stubber_cli

##########################################################################################
# log = logging.getLogger("stubber")
#########################################################################################


@stubber_cli.command(name="stub")
@click.option("--source", "-s", type=click.Path(exists=True, file_okay=True, dir_okay=True))
def cli_stub(source: Union[str, Path]):
    "Create or update .pyi type hint files."

    log.info("Generate type hint files (pyi) in folder: {}".format(source))
    OK = generate_pyi_files(Path(source))
    # do not generate pyi files twice
    do_post_processing([Path(source)], stubgen=False, black=True, autoflake=False)
    return 0 if OK else 1
