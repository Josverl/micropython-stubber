"""
prepare a set of stub files for publishing to PyPi

"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Union

from loguru import logger as log
from packaging.version import parse
from pysondb import PysonDB
from stubber.publish.enums import COMBO_STUBS, CORE_STUBS, DOC_STUBS, StubSource
from stubber.publish.stubpacker import StubPackage
from stubber.utils.versions import clean_version

# replace std log handler with a custom one capped on INFO level
log.remove()
log.add(sys.stderr, level="INFO", backtrace=True, diagnose=True)


def package_name(pkg_type, port: str = "", board: str = "", family="micropython", **kwargs) -> str:
    "generate a package name for the given package type"
    if pkg_type == COMBO_STUBS:
        # # {family}-{port}-{board}-stubs
        return f"{family}-{port}-{board}-stubs".lower().replace("-generic-stubs", "-stubs")
    elif pkg_type == DOC_STUBS:
        return f"{family}-doc-stubs".lower()
    elif pkg_type == CORE_STUBS:
        return f"{family}-core-stubs".lower()

    raise NotImplementedError(port, board, pkg_type)


# def package_path(port, board, mpy_version, pub_path: Path, pkg=COMBINED, family="micropython") -> Path:
#     "generate a package name"
#     return pub_path / package_name( port, board, pkg, family)


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

    # [
    #     log.trace(
    #         f"{x['data']['name']} - {x['data']['mpy_version']} - {x['data']['pkg_version']}"
    #     )
    #     for x in packages
    # ]
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
) -> StubPackage:
    """
    create and initialize a package with the correct sources

    """
    package = None
    if pkg_type == COMBO_STUBS:
        assert port != ""
        assert board != ""
        ver_flat = clean_version(mpy_version, flat=True)
        stubs: List[Tuple[str, Path]] = [
            (
                StubSource.FIRMWARE,
                # TODO: look for the most specific firmware stub folder that is available ?
                # is it possible to prefer micropython-nrf-microbit-stubs over micropython-nrf-stubs
                # that would also require the port - board - variant to be discoverable runtime
                Path(f"{family}-{ver_flat}-{port}"),
            ),
            (
                StubSource.FROZEN,
                Path(f"{family}-{ver_flat}-frozen") / port / board,
            ),
            (
                StubSource.CORE,
                Path("cpython_core-pycopy"),
            ),
        ]
        package = StubPackage(pkg_name, version=mpy_version, stubs=stubs)
    elif pkg_type == DOC_STUBS:
        # TODO add doc stubs
        ver_flat = clean_version(mpy_version, flat=True)

        stubs: List[Tuple[str, Path]] = [
            (
                "Doc stubs",
                Path(f"{family}-{ver_flat}-docstubs"),
            ),
        ]
        package = StubPackage(pkg_name, version=mpy_version, stubs=stubs)

    elif pkg_type == CORE_STUBS:
        # TODO add core stubs
        raise NotImplementedError(type)
    else:
        raise NotImplementedError(type)

    return package
