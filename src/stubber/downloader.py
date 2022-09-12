"Download files from a public github repo"
# Copyright (c) 2020 Jos Verlinde
# MIT license
# pylint: disable= invalid-name
import os

import requests
from loguru import logger as log

# # log = logging.getLogger(__name__)
# log.setLevel(level=logging.INFO)


def download_file(url: str, module: str, folder: str = "./"):
    "dowload a file from a public github repo"
    local_filename = os.path.abspath(os.path.join(folder, module))
    log.debug("Downloading {:<20} to {}".format(module, local_filename))
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    return local_filename


def download_files(repo, frozen_modules, savepath):
    "dowload multiple files from a public github repo"
    if not os.path.exists(savepath):
        os.makedirs(savepath)

    for mod in frozen_modules:
        url = repo.format(mod)
        download_file(url, mod, savepath)
