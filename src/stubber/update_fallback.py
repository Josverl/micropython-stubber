import os
import shutil
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError
from pathlib import Path
from typing import List, Optional, Tuple

from loguru import logger as log

# log = logging.getLogger()

RELEASED = "v1_18"


def fallback_sources(version: str, fw_version: Optional[str] = None) -> List[Tuple[str, str]]:
    """
    list of sources to build/update the fallback 'catch-all' stubfolder
    version : the version to use
    fw_version : version to source the Firmware stubs from.  defaults to the version used , but can be lower

    """
    if not fw_version:
        fw_version = version
    if fw_version == "latest":
        fw_version = RELEASED
    SOURCES = [
        ("uasyncio", f"micropython-{fw_version}-esp32"),
        ("umqtt", f"micropython-{fw_version}-esp32"),
        ("_onewire.py*", f"micropython-{fw_version}-esp32"),
        ("_uasyncio.py*", f"micropython-{fw_version}-esp32"),
        ("array.py*", f"micropython-{fw_version}-esp32"),
        ("binascii.py*", f"micropython-{fw_version}-esp32"),
        ("hashlib.py*", f"micropython-{fw_version}-esp32"),
        ("machine.py*", f"micropython-{fw_version}-esp32"),
        ("micropython.py*", f"micropython-{version}-docstubs"),  # esp32"),
        ("network.pyi", f"micropython-{version}-docstubs"),  # esp32"),
        ("struct.py*", f"micropython-{fw_version}-esp32"),
        ("uarray.py*", f"micropython-{fw_version}-esp32"),
        ("ubinascii.py*", f"micropython-{fw_version}-esp32"),
        ("uctypes.py*", f"micropython-{fw_version}-esp32"),
        ("uerrno.py*", f"micropython-{fw_version}-esp32"),
        ("uhashlib.py*", f"micropython-{fw_version}-esp32"),
        ("uio.py*", f"micropython-{fw_version}-esp32"),
        ("ujson.py*", f"micropython-{fw_version}-esp32"),
        ("uselect.py*", f"micropython-{fw_version}-esp32"),
        ("usocket.py*", f"micropython-{fw_version}-esp32"),
        ("ussl.py*", f"micropython-{fw_version}-esp32"),
        ("ustruct.py*", f"micropython-{fw_version}-esp32"),
        ("sys.py*", f"micropython-{fw_version}-esp32"),
        ("usys.py*", f"micropython-{fw_version}-esp32"),
        ("uzlib.py*", f"micropython-{fw_version}-esp32"),
        ("bluetooth.py*", f"micropython-{version}-docstubs"),
        # esp
        ("esp.py*", f"micropython-{version}-docstubs"),  # 8266 fw stub has most functions
        ("esp32.py*", f"micropython-{version}-docstubs"),  # esp32"),
        # pyboard == stm32
        ("pyb.py*", f"micropython-{fw_version}-stm32"),
        ("framebuf.py*", f"micropython-{fw_version}-stm32"),
        # rp2
        ("_rp2.py*", f"micropython-{fw_version}-rp2"),
        # stdlib
        ("os.py*", f"micropython-{fw_version}-esp32"),  # -> stdlib
        ("uos.py*", f"micropython-{fw_version}-esp32"),
        ("time.py*", f"micropython-{fw_version}-esp32"),  # -> stdlib
        ("utime.py*", f"micropython-{fw_version}-esp32"),
    ]
    return SOURCES


def update_fallback(stubpath: Path, fallback_path: Path, version: str = RELEASED):
    "update the fallback stubs from the defined sources"
    # remove all *.py/.pyi files
    if not fallback_path.exists():
        os.makedirs(fallback_path)
    else:
        oldstubs = list(fallback_path.rglob("*.py")) + list(fallback_path.rglob("*.pyi"))
        log.debug(f"deleting {len(oldstubs)} stubs from {fallback_path.as_posix()}")
        for f in oldstubs:
            try:
                os.remove(f)
            except OSError as e:
                log.warning(e)
    added = 0
    for (name, source) in fallback_sources(version):
        if not "." in name:
            # copy folder
            log.debug(f"add {source} folder")
            try:
                copy_tree(
                    (stubpath / source / name).as_posix(),
                    (fallback_path / name).as_posix(),
                )
                added += 1
            except DistutilsFileError:
                log.warning(f"{(stubpath / source / name).as_posix()} not found")
        else:
            # copy file(s)
            log.debug(f"add {source}")
            for f in (stubpath / source).glob(name):
                shutil.copyfile(f, fallback_path / f.name)
                added += 1
    return added


if __name__ == "__main__":
    from stubber.utils.config import CONFIG

    update_fallback(
        CONFIG.stub_path,
        CONFIG.fallback_path,
        version=RELEASED,
    )
