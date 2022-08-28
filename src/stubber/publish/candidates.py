import re
from itertools import chain
from pathlib import Path
from typing import List, Union

from stubber.publish.publish_stubs import COMBO_STUBS, CORE_STUBS, DOC_STUBS
from stubber.utils.versions import clean_version


def subfolder_names(path: Path):
    "returns a list of names of the subfolders of the given path"
    if path.exists():
        for child in path.iterdir():
            if child.is_dir():
                yield child.name


def version_cadidates(suffix: str, prefix=r".*", *, path=Path("stubs")):
    "get a list of versions for the given family and suffix"
    if path.exists():
        folder_re = prefix + "-(.*)-" + suffix
        for name in subfolder_names(path):
            match = re.match(folder_re, name)
            if match:
                yield clean_version(match.group(1))


def frozen_candidates(
    family: str = "micropython",
    versions: Union[str, List[str]] = "latest",
    ports: Union[str, List[str]] = "auto",
    boards: Union[str, List[str]] = "auto",
    *,
    path=Path("stubs"),
):  # -> Generator[dict[str,str], None, None]:
    """
    generate a list of possible firmware stubs for the given family (, version port and board) ?
    - family = micropython
        board and port are ignored, they are looked up from the available frozen stubs
    """
    auto_port = isinstance(ports, str) and "auto" == ports
    auto_board = isinstance(boards, str) and "auto" == boards
    auto_version = isinstance(versions, str) and "auto" == versions

    if isinstance(versions, str):
        if auto_version:
            versions = list(version_cadidates(suffix="frozen", prefix=family, path=path))
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
            if auto_board:
                if family == "micropython":
                    # lookup the (frozen) micropython ports
                    boards_path = path / f"{family}-{version}-frozen" / port
                    boards = list(subfolder_names(boards_path))
                else:
                    raise NotImplementedError(f"auto boards not implemented for family {family}")  # pragma: no cover
                # elif family == "pycom":
                #     boards = ["wipy", "lopy", "gpy", "fipy"]
            # ---------------------------------------------------------------------------
            for board in boards:
                if (path / f"{family}-{version}-frozen" / port / board).exists():
                    yield {"family": family, "version": version, "port": port, "board": board, "pkg_type": COMBO_STUBS}


def docstub_candidates(
    family: str = "micropython",
    versions: Union[str, List[str]] = "latest",
    path=Path("stubs"),
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
