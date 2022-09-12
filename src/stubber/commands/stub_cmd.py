##########################################################################################
# stub
##########################################################################################

from loguru import logger as log
from pathlib import Path
from typing import Union

import click
import stubber.utils as utils

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
    return 0 if OK else 1
