"""Pre/Post Processing for createstubs.py"""
from typing import List
from pathlib import Path
import sys
import subprocess
import logging
from .stubmaker import generate_pyi_files

log = logging.getLogger(__name__)


def do_post_processing(stub_paths: List[Path], pyi: bool, black: bool):
    "Common post processing"
    for pth in stub_paths:
        if pyi:
            log.info("Generate type hint files (pyi) in folder: {}".format(pth))
            generate_pyi_files(pth)
        if black:
            run_black(pth)


def run_black(path: Path):
    try:
        cmd = ["black", "."]

        if sys.version_info.major == 3 and sys.version_info.minor <= 7:
            # black on python 3.7 does not like some function defs
            # def sizeof(struct, layout_type=NATIVE, /) -> int:
            cmd += ["--fast"]
        # capture to suppress based on log level
        result = subprocess.run(cmd, capture_output=log.level >= logging.INFO, check=True, shell=False, cwd=path)
        if result.returncode != 0:  pragma: no cover #
            raise Exception(result.stderr.decode("utf-8"))
    except subprocess.SubprocessError:  # pragma: no cover
        log.error("some of the files are not in a proper format")
