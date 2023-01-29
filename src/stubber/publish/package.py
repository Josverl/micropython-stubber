"""
prepare a set of stub files for publishing to PyPi

"""
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Union

from loguru import logger as log
from packaging.version import parse
from pysondb import PysonDB

from stubber.publish.enums import (COMBO_STUBS, CORE_STUBS, DOC_STUBS,
                                   StubSource)
from stubber.publish.stubpacker import StubPackage
from stubber.utils.config import CONFIG
from stubber.utils.versions import clean_version

GENERIC = "generic"

# replace std log handler with a custom one capped on INFO level
log.remove()
log.add(sys.stderr, level="INFO", backtrace=True, diagnose=True)


def package_name(pkg_type: str, *, port: str = "", board: str = "", family="micropython", **kwargs) -> str:
    "generate a package name for the given package type"
    if pkg_type == COMBO_STUBS:
        # # {family}-{port}-{board}-stubs
        name = f"{family}-{port}-{board}-stubs".lower()
        name = name.replace("-generic-stubs", "-stubs")
        name = name.replace("-generic_", "-")
        return name
    elif pkg_type == DOC_STUBS:
        return f"{family}-doc-stubs".lower()
    elif pkg_type == CORE_STUBS:
        return f"{family}-core-stubs".lower()
    # # {family}-{port}-{board}-{type}-stubs
    name = f"{family}-{port}-{board}-{pkg_type}-stubs".lower()
    # remove -generic- from the name
    name = name.replace(f"-generic-{pkg_type}-stubs", f"-{pkg_type}-stubs")
    # remove -genetic_ from the name
    name = name.replace("-generic_", "-")
    return name


def get_package(
    db: PysonDB,
    *,
    pkg_type,
    version: str,
    port: str,
    board: str = GENERIC,
    family: str = "micropython",
) -> StubPackage:
    """Get the package from the database or create a new one if it does not exist."""
    pkg_name = package_name(pkg_type, port=port, board=board, family=family)
    version = clean_version(version, drop_v=True)
    if package_info := get_package_info(
        db,
        CONFIG.publish_path,
        pkg_name=pkg_name,
        mpy_version=version,
    ):
        # create package from the information retrieved from the database
        return StubPackage(pkg_name, version=version, json_data=package_info)

    log.debug(f"No package found for {pkg_name} in database, creating new package")
    return create_package(
        pkg_name,
        mpy_version=version,
        port=port,
        board=board,
        family=family,
        pkg_type=pkg_type,
    )


def get_package_info(db: PysonDB, pub_path: Path, *, pkg_name: str, mpy_version: str) -> Union[Dict, None]:
    """
    get a package's record from the json db if it can be found
    matches om the package name and version
        pkg_name: package name (micropython-esp32-stubs)
        mpy_version: micropython/firmware version (1.18)
    """
    # find in the database
    recs = db.get_by_query(query=lambda x: x["mpy_version"] == mpy_version and x["name"] == pkg_name)
    # dict to list
    recs = [{"id": key, "data": recs[key]} for key in recs]
    # sort
    packages = sorted(recs, key=lambda x: parse(x["data"]["pkg_version"]))

    if len(packages) > 0:
        pkg_from_db = packages[-1]["data"]
        log.debug(f"Found latest {pkg_name} == {pkg_from_db['pkg_version']}")
        return pkg_from_db
    else:
        return None


def create_package(
    pkg_name: str,
    mpy_version: str,
    *,
    port: str = "",
    board: str = "",
    family: str = "micropython",
    pkg_type=COMBO_STUBS,
) -> StubPackage:  # sourcery skip: merge-duplicate-blocks, remove-redundant-if
    """
    create and initialize a package with the correct sources
    """
    ver_flat = clean_version(mpy_version, flat=True)
    if pkg_type == COMBO_STUBS:
        assert port != "", "port must be specified for combo stubs"
        # Use lower case for paths to avoid case sensitive issues
        port = port.lower()
        # BOARD in the micropython repo is always uppercase by convention (GENERIC)
        # but MUST  be used in lowercase in the stubs repo
        board = board.lower() if board else GENERIC
        stubs: List[Tuple[str, Path]] = []
        stubs= [
            (
                # StubSource.FIRMWARE,
                # Path(f"{family}-{ver_flat}-{port}"),
                # TODO: look for the most specific firmware stub folder that is available ?
                # is it possible to prefer micropython-nrf-microbit-stubs over micropython-nrf-stubs
                # that would also require the port - board - variant to be discoverable runtime
                StubSource.MERGED,
                Path(f"{family}-{ver_flat}-{port}-{board}-merged") if board != GENERIC else Path(f"{family}-{ver_flat}-{port}-merged"),
            ),
            (
                StubSource.FROZEN,
                Path(f"{family}-{ver_flat}-frozen") / port / board.upper(), # BOARD in source frozen path needs to be UPPERCASE
            ),
            (
                StubSource.CORE,
                Path("micropython_core"),  # TODO : Add version to core stubs
            ),
        ]
    elif pkg_type == DOC_STUBS:
        # TODO add doc stubs
        stubs= [
            (
                "Doc stubs",
                Path(f"{family}-{ver_flat}-docstubs"),
            ),
        ]
    elif pkg_type == CORE_STUBS:
        # TODO add core stubs
        raise NotImplementedError(type)
    else:
        raise NotImplementedError(type)

    return StubPackage(pkg_name, version=mpy_version, stubs=stubs)
