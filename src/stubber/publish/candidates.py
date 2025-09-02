"""
In order to generate stups for all ports and boars and versions of micropython we need to know
what versions are available. This module provides functions to :
    - get a list of all ports for a given version of micropython  ( list micropython ports)
    - get a list of all ports and board for a given version of micropython (list micropython ports boards)

        - get a list of versions for micropython ( version candidates)
    - get the frozen stubs for a given version of micropython ( frozen candidates)
    - get a list of all the docstubs (docstub candidates)
    - get a list of the firmware/MCU stubs (firmware candidates)
"""

import re
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union

from mpflash.logger import log
from packaging.version import parse

import mpflash.basicgit as git
from mpflash.versions import (
    OLDEST_VERSION,
    SET_PREVIEW,
    V_PREVIEW,
    clean_version,
    micropython_versions,
)
from stubber import utils
from stubber.publish.defaults import GENERIC, GENERIC_L, GENERIC_U

# from stubber.publish.enums import COMBO_STUBS
from stubber.utils.config import CONFIG


def subfolder_names(path: Path):
    "returns a list of names of the sub folders of the given path"
    if path.exists():
        for child in path.iterdir():
            if child.is_dir():
                yield child.name


def version_candidates(
    suffix: str,
    prefix: str = r".*",
    *,
    path: Path = CONFIG.stub_path,
    oldest: str = OLDEST_VERSION,
) -> Generator[str, None, None]:
    "get a list of versions for the given family and suffix"
    if path.exists():
        folder_re = prefix + "-(.*)-" + suffix
        for name in subfolder_names(path):
            if match := re.match(folder_re, name):
                folder_ver = clean_version(match[1])
                if folder_ver == V_PREVIEW or parse(folder_ver) >= parse(oldest):
                    yield folder_ver


def list_frozen_ports(
    family: str = "micropython",
    version: str = V_PREVIEW,
    path: Path = CONFIG.stub_path,
):
    "get list of ports with frozen stubs for a given family and version"
    ports_path = path / f"{family}-{version}-frozen"
    return list(subfolder_names(ports_path))


def list_micropython_ports(
    family: str = "micropython",
    mpy_path: Path = CONFIG.mpy_path,
):
    "get list of micropython ports for a given family and version"
    if family != "micropython":
        # todo: add support for other families
        return []
    mpy_path = Path("./repos/micropython")

    ports_path = mpy_path / "ports"
    return [p for p in list(subfolder_names(ports_path)) if p not in CONFIG.BLOCKED_PORTS]


def list_micropython_port_boards(
    port: str,
    family: str = "micropython",
    mpy_path: Path = CONFIG.mpy_path,
):
    "get list of micropython boards for a given family version and board"
    if family != "micropython":
        # todo: add support for other families
        return []
    mpy_path = Path("./repos/micropython")
    boards_path = mpy_path / "ports" / port / "boards"
    return list(subfolder_names(boards_path))


def frozen_candidates(
    family: str = "micropython",
    versions: Union[str, List[str]] = V_PREVIEW,
    ports: Union[str, List[str]] = "all",
    boards: Union[str, List[str]] = "all",
    *,
    path: Path = CONFIG.stub_path,
) -> Generator[Dict[str, Any], None, None]:
    """
    generate a list of possible MCU stubs for the given family (, version port and board) ?
    - family = micropython
        board and port are ignored, they are looked up from the available frozen stubs
    - versions = 'latest' , 'auto' or a list of versions
    - port = 'auto' or a specific port
    - board = 'auto' or a specific board, 'generic' must be specified in lowercare
    """
    auto_port = is_auto(ports)
    auto_board = is_auto(boards)
    if is_auto(versions):
        versions = list(version_candidates(suffix="frozen", prefix=family, path=path)) + [
            V_PREVIEW
        ]
    else:
        versions = [versions] if isinstance(versions, str) else versions

    versions = [clean_version(v, flat=True) for v in versions]

    if isinstance(ports, str):
        ports = [ports]
    if isinstance(boards, str):
        boards = [boards]
    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------
    for version in versions:
        if auto_port:
            if family == "micropython":
                # lookup the (frozen) micropython ports
                ports = list_frozen_ports(family, version, path=path)
            else:
                raise NotImplementedError(
                    f"auto ports not implemented for family {family}"
                )  # pragma: no cover
            # elif family == "pycom":
            #     ports = ["esp32"]
            # elif family == "lobo":
            #     ports = ["esp32"]
        # ---------------------------------------------------------------------------
        for port in ports:
            port_path = path / f"{family}-{version}-frozen" / port
            if port_path.exists():
                yield {
                    "family": family,
                    "version": version,
                    "port": port,
                    "board": GENERIC_L,
                    # "pkg_type": COMBO_STUBS,
                }
            # if not auto_board:
            #     for board in boards:
            #         port_path = board_path/ "board" / board
            #         if port_path.exists():
            #             yield {"family": family, "version": version, "port": port, "board": board, "pkg_type": COMBO_STUBS}
            # else: # auto board
            if auto_board:
                if family == "micropython":
                    # lookup the (frozen) micropython ports
                    boards = list(subfolder_names(port_path))
                    # TODO: remove non-relevant boards
                    # - release - used in release testing
                    # generic_512 - small memory footprint
                    #

                else:
                    # raise NotImplementedError(f"auto boards not implemented for family {family}")  # pragma: no cover
                    raise NotImplementedError(
                        f"auto boards not implemented for family {family}"
                    )  # pragma: no cover
                # elif family == "pycom":
                #     boards = ["wipy", "lopy", "gpy", "fipy"]
            # ---------------------------------------------------------------------------
            for board in boards:
                assert isinstance(board, str)
                # frozen stubs found, and not excluded, generic is already explicitly included, test builds excluded
                # Micropython repo uses CAPS for board names, but micropython-stubs are lowercase
                board_found = (path / f"{family}-{version}-frozen" / port / board.upper()).exists()
                if board_found and board.upper() not in [
                    GENERIC_L.upper(),
                    "RELEASE",
                    "GENERIC_512K",
                ]:
                    yield {
                        "family": family,
                        "version": version,
                        "port": port,
                        "board": board,
                        # "pkg_type": COMBO_STUBS,
                    }


def is_auto(thing: Union[None, str, List[str]]):
    "Is this version/port/board specified as 'auto' ?"
    if isinstance(thing, str):
        return thing in ["auto", "all"]
    if isinstance(thing, list):
        return any(i in ["auto", "all"] for i in thing)


def board_candidates(
    family: str = "micropython",
    versions: Union[str, List[str]] = V_PREVIEW,
    *,
    mpy_path: Path = CONFIG.mpy_path,
):
    """
    generate a list of possible board stub candidates for the given family and version.
    list is based on the micropython repo:  /ports/<list of ports>/boards/<list of boards>
    """
    if is_auto(versions):
        versions = list(micropython_versions(minver=OLDEST_VERSION))
    elif isinstance(versions, str):
        versions = [versions]
    versions = [clean_version(v, flat=False) for v in versions]

    for version in versions:
        # check out the micropython repo for this version
        if version in SET_PREVIEW:
            r = git.switch_branch(repo=mpy_path, branch="master")
            # get the current checked out version
            version = utils.checkedout_version(mpy_path)
        else:
            r = git.checkout_tag(repo=mpy_path, tag=version)
        if not r:
            log.warning(
                f"Incorrect version: {version} or did you forget to run `stubber clone` to get the micropython repo?"
            )
            return []
        ports = list_micropython_ports(family=family, mpy_path=mpy_path)
        for port in ports:
            # Yield the generic port exactly one time
            yield {
                "family": family,
                "version": version,
                "port": port,
                "board": GENERIC_U,
            }
            for board in list_micropython_port_boards(family=family, mpy_path=mpy_path, port=port):
                if board not in GENERIC:
                    yield {
                        "family": family,
                        "version": version,
                        "port": port,
                        "board": board,
                    }


def filter_list(
    worklist: List[Dict[str, str]],
    ports: Optional[Union[List[str], str]] = None,
    boards: Optional[Union[List[str], str]] = None,
    # versions: Optional[Union[List[str], str]] = None,
):
    """
    filter a list of candidates down to the ones we want, based on the ports and boards specified (case insensitive)
    for board also match using a 'GENERIC_' prefix, so board 's3' will match candidate 'GENERIC_S3'
    """
    worklist = [i for i in worklist if i["board"] != ""]
    if ports and not is_auto(ports):
        ports_ = [i.lower() for i in ports]
        worklist = [i for i in worklist if i["port"].lower() in ports_]
    if boards and not is_auto(boards):
        boards_ = [i.lower() for i in boards]
        worklist = [
            i
            for i in worklist
            if i["board"].lower() in boards_
            or i["board"].lower().replace("generic_", "") in boards_
        ]
    return worklist
