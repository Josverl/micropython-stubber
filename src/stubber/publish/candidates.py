import re
from pathlib import Path
from typing import Any, Dict, Generator, List, Union

import stubber.basicgit as git
from packaging.version import parse
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


def version_cadidates(suffix: str, prefix=r".*", *, path=CONFIG.stub_path, oldest=OLDEST_VERSION) -> Generator[str, None, None]:
    "get a list of versions for the given family and suffix"
    if path.exists():
        folder_re = prefix + "-(.*)-" + suffix
        for name in subfolder_names(path):
            match = re.match(folder_re, name)
            if match:
                folder_ver = clean_version(match.group(1))
                if folder_ver == V_LATEST or parse(folder_ver) >= parse(oldest):
                    yield folder_ver


def list_frozen_ports(
    family: str = "micropython",
    version: str = V_LATEST,
    path=CONFIG.stub_path,
):
    "get list of ports with frozen stubs for a given family and version"
    ports_path = path / f"{family}-{version}-frozen"
    ports = list(subfolder_names(ports_path))
    return ports


def list_micropython_ports(
    family: str = "micropython",
    version: str = V_LATEST[0],
    mpy_path=CONFIG.mpy_path,
):
    "get list of micropython ports for a given family and version"
    if family != "micropython":
        # todo: add support for other families
        return []
    mpy_path = Path("./repos/micropython")
    # check out the micropthon repo for this version
    if not git.checkout_tag(version, mpy_path):
        return []
    ports_path = mpy_path / "ports"
    ports = list(subfolder_names(ports_path))
    # remove blocked ports from list
    for port in ["minimal", "bare-arm"]:  # CONFIG.blocked_ports:
        if port in ports:
            ports.remove(port)
    return ports


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
    - board = 'auto' or a specific board, 'GENERIC' shoould be specifid in CAPS
    """
    auto_port = isinstance(ports, str) and "auto" == ports or isinstance(ports, list) and "auto" in ports
    auto_board = isinstance(boards, str) and "auto" == boards or isinstance(boards, list) and "auto" in boards
    auto_version = isinstance(versions, str) and "auto" == versions or isinstance(versions, list) and "auto" in versions

    if isinstance(versions, str):
        if auto_version:
            versions = list(version_cadidates(suffix="frozen", prefix=family, path=path)) + [V_LATEST]
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
            boards_path = path / f"{family}-{version}-frozen" / port
            if boards_path.exists():
                yield {"family": family, "version": version, "port": port, "board": "GENERIC", "pkg_type": COMBO_STUBS}
            if auto_board:
                if family == "micropython":
                    # lookup the (frozen) micropython ports
                    boards = list(subfolder_names(boards_path))
                    # TODO: remove non-relevant boards
                    # - release - used in release testing
                    # generic_512 - small memory footprint
                    #

                else:
                    # raise NotImplementedError(f"auto boards not implemented for family {family}")  # pragma: no cover
                    raise Exception(f"auto boards not implemented for family {family}")  # pragma: no cover
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
        if "auto" == versions:  # auto with vprefix ...
            versions = list(version_cadidates(suffix="docstubs", prefix=family, path=path))
        else:
            versions = [versions]
    versions = [clean_version(v, flat=True) for v in versions]

    for version in versions:
        yield {"family": family, "version": version, "pkg_type": DOC_STUBS}


def firmware_candidates(
    family: str = "micropython",
    versions: Union[str, List[str]] = V_LATEST,
    *,
    mpy_path=CONFIG.mpy_path,
):
    """generate a list of possible firmware stub candidates for the given family and version."""
    if isinstance(versions, str):
        if "auto" == versions:  # auto with vprefix ...
            versions = list(micropython_versions(start=OLDEST_VERSION))
        else:
            versions = [versions]
    versions = [clean_version(v, flat=False) for v in versions]

    for version in versions:
        ports = list_micropython_ports(family, version, mpy_path=mpy_path)
        for port in ports:
            yield {"family": family, "version": version, "port": port, "board": "", "pkg_type": FIRMWARE_STUBS}
