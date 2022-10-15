##########################################################################################
# stub
##########################################################################################

from loguru import logger as log
from pathlib import Path
from typing import Union

import click
import stubber.utils as utils
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
    OK = utils.generate_pyi_files(Path(source))
    do_post_processing([Path(source)], pyi=True, black=True)
    return 0 if OK else 1
