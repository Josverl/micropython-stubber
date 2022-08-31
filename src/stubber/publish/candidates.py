import re
from pathlib import Path
from typing import Any, Generator, List, Union

from packaging.version import parse
from stubber.publish.package import COMBO_STUBS, CORE_STUBS, DOC_STUBS
from stubber.utils.config import CONFIG
from stubber.utils.versions import clean_version

OLDEST_VERSION = "1.16"
"oldest versions of the stubs"

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


def frozen_candidates(
    family: str = "micropython",
    versions: Union[str, List[str]] = V_LATEST,
    ports: Union[str, List[str]] = "auto",
    boards: Union[str, List[str]] = "auto",
    *,
    path=CONFIG.stub_path,
) -> Generator[dict[str, Any], None, None]:
    """
    generate a list of possible firmware stubs for the given family (, version port and board) ?
    - family = micropython
        board and port are ignored, they are looked up from the available frozen stubs
    - versions = 'latest' , 'auto' or a list of versions
    - port = 'auto' or a specific port
    - board = 'auto' or a specific board, 'GENERIC' shoould be specifid in CAPS
    """
    auto_port = isinstance(ports, str) and "auto" == ports
    auto_board = isinstance(boards, str) and "auto" == boards
    auto_version = isinstance(versions, str) and "auto" == versions

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
                ports_path = path / f"{family}-{version}-frozen"
                ports = list(subfolder_names(ports_path))
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

    Note that the folders do not need to exist, with the exaption of auto which will scan the stubs folder for versions of docstubs
    """
    if isinstance(versions, str):
        if "auto" == versions:  # auto with vprefix ...
            versions = list(version_cadidates(suffix="docstubs", prefix=family, path=path))
        else:
            versions = [versions]
    versions = [clean_version(v, flat=True) for v in versions]

    for version in versions:
        yield {"family": family, "version": version, "pkg_type": DOC_STUBS}
