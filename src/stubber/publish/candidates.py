import re
from pathlib import Path
from typing import Any, Dict, Generator, List, Union

from packaging.version import parse

import stubber.basicgit as git
from stubber.publish.enums import COMBO_STUBS, DOC_STUBS, FIRMWARE_STUBS
from stubber.utils.config import CONFIG
from stubber.utils.versions import clean_version, micropython_versions

OLDEST_VERSION = "1.16"
"This is the oldest MicroPython version to build the stubs on"

V_LATEST = "latest"


def subfolder_names(path: Path):
    "returns a list of names of the subfolders of the given path"
    if path.exists():
        for child in path.iterdir():
            if child.is_dir():
                yield child.name


def version_candidates(suffix: str, prefix=r".*", *, path=CONFIG.stub_path, oldest=OLDEST_VERSION) -> Generator[str, None, None]:
    "get a list of versions for the given family and suffix"
    if path.exists():
        folder_re = prefix + "-(.*)-" + suffix
        for name in subfolder_names(path):
            if match := re.match(folder_re, name):
                folder_ver = clean_version(match[1])
                if folder_ver == V_LATEST or parse(folder_ver) >= parse(oldest):
                    yield folder_ver


def list_frozen_ports(
    family: str = "micropython",
    version: str = V_LATEST,
    path=CONFIG.stub_path,
):
    "get list of ports with frozen stubs for a given family and version"
    ports_path = path / f"{family}-{version}-frozen"
    return list(subfolder_names(ports_path))


def list_micropython_ports(
    family: str = "micropython",
    mpy_path=CONFIG.mpy_path,
):
    "get list of micropython ports for a given family and version"
    if family != "micropython":
        # todo: add support for other families
        return []
    mpy_path = Path("./repos/micropython")

    ports_path = mpy_path / "ports"
    ports = list(subfolder_names(ports_path))
    # remove blocked ports from list
    for port in ["minimal", "bare-arm"]:  # CONFIG.blocked_ports:
        if port in ports:
            ports.remove(port)
    return ports


def list_micropython_port_boards(
    port: str,
    family: str = "micropython",
    mpy_path=CONFIG.mpy_path,
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
    versions: Union[str, List[str]] = V_LATEST,
    ports: Union[str, List[str]] = "auto",
    boards: Union[str, List[str]] = "auto",
    *,
    path=CONFIG.stub_path,
) -> Generator[Dict[str, Any], None, None]:
    """
    generate a list of possible firmware stubs for the given family (, version port and board) ?
    - family = micropython
        board and port are ignored, they are looked up from the available frozen stubs
    - versions = 'latest' , 'auto' or a list of versions
    - port = 'auto' or a specific port
    - board = 'auto' or a specific board, 'GENERIC' must be specified in ALLCAPS
    """
    auto_port = (
        isinstance(ports, str)
        and ports == "auto"
        or isinstance(ports, list)
        and "auto" in ports
    )
    auto_board = (
        isinstance(boards, str)
        and boards == "auto"
        or isinstance(boards, list)
        and "auto" in boards
    )
    if isinstance(versions, str):
        auto_version = (
            versions == "auto"
            or isinstance(versions, list)
            and "auto" in versions
        )

        if auto_version:
            versions = list(version_candidates(suffix="frozen", prefix=family, path=path)) + [V_LATEST]
        else:
            versions = [versions]
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
                raise NotImplementedError(f"auto ports not implemented for family {family}")  # pragma: no cover
            # elif family == "pycom":
            #     ports = ["esp32"]
            # elif family == "lobo":
            #     ports = ["esp32"]
        # ---------------------------------------------------------------------------
        for port in ports:
            board_path = path / f"{family}-{version}-frozen" / port
            if board_path.exists():
                yield {"family": family, "version": version, "port": port, "board": "GENERIC", "pkg_type": COMBO_STUBS}
            # if not auto_board:
            #     for board in boards:
            #         port_path = board_path/ "board" / board
            #         if port_path.exists():
            #             yield {"family": family, "version": version, "port": port, "board": board, "pkg_type": COMBO_STUBS}
            # else: # auto board
            if auto_board:
                if family == "micropython":
                    # lookup the (frozen) micropython ports
                    boards = list(subfolder_names(board_path))
                    # TODO: remove non-relevant boards
                    # - release - used in release testing
                    # generic_512 - small memory footprint
                    #

                else:
                    # raise NotImplementedError(f"auto boards not implemented for family {family}")  # pragma: no cover
                    raise NotImplementedError(f"auto boards not implemented for family {family}")  # pragma: no cover
                # elif family == "pycom":
                #     boards = ["wipy", "lopy", "gpy", "fipy"]
            # ---------------------------------------------------------------------------
            for board in boards:
                assert isinstance(board, str)
                # prozen stubs found , and not excluded, generic is already explicitly included
                if (path / f"{family}-{version}-frozen" / port / board).exists() and board.upper() not in [
                    "GENERIC",
                    "RELEASE",
                    "GENERIC_512K",
                ]:
                    yield {"family": family, "version": version, "port": port, "board": board, "pkg_type": COMBO_STUBS}


def docstub_candidates(
    family: str = "micropython",
    versions: Union[str, List[str]] = V_LATEST,
    path=CONFIG.stub_path,
):
    """generate a list of possible documentation stub candidates for the given family and version.

    Note that the folders do not need to exist, with the exeption of auto which will scan the stubs folder for versions of docstubs
    """
    if isinstance(versions, str):
        if versions == "auto":  # auto with vprefix ...
            versions = list(version_candidates(suffix="docstubs", prefix=family, path=path))
        else:
            versions = [versions]
    versions = [clean_version(v, flat=True) for v in versions]

    for version in versions:
        yield {"family": family, "version": version, "pkg_type": DOC_STUBS}


def firmware_candidates(
    family: str = "micropython", versions: Union[str, List[str]] = V_LATEST, *, mpy_path=CONFIG.mpy_path, pt=FIRMWARE_STUBS
):
    """
    generate a list of possible firmware stub candidates for the given family and version.
    list is basesed on the micropython repo
    /ports/<list of ports>/boards/<list of boards>
    """
    if isinstance(versions, str):
        if versions == "auto":  # auto with vprefix ...
            versions = list(micropython_versions(start=OLDEST_VERSION))
        else:
            versions = [versions]
    versions = [clean_version(v, flat=False) for v in versions]

    for version in versions:
        # check out the micropthon repo for this version
        if version in ["latest", "master"]:
            r = git.switch_branch(repo=mpy_path, branch="master")
        else:
            r = git.checkout_tag(repo=mpy_path, tag=version)
        if not r:
            return []
        ports = list_micropython_ports(family=family, mpy_path=mpy_path)
        for port in ports:
            yield {"family": family, "version": version, "port": port, "board": "GENERIC", "pkg_type": pt}
            for board in list_micropython_port_boards(family=family, mpy_path=mpy_path, port=port):
                yield {"family": family, "version": version, "port": port, "board": board, "pkg_type": pt}
