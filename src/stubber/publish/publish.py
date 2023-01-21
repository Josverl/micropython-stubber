"""
prepare a set of stub files for publishing to PyPi

!!Note: anything excluded in .gitignore is not packaged by poetry
"""
from typing import Any, Dict, List
from loguru import logger as log

from stubber.publish.candidates import firmware_candidates
from stubber.publish.database import get_database
from stubber.publish.enums import COMBO_STUBS
from stubber.publish.package import create_package, get_package_info, package_name
from stubber.publish.stubpacker import StubPackage
from stubber.utils.config import CONFIG

from pysondb import PysonDB 

def get_package(db:PysonDB, *, pkg_type, version:str, port:str, board:str="GENERIC", family:str="micropython",) -> StubPackage:
    """Get the package from the database or create a new one if it does not exist."""
    pkg_name = package_name(pkg_type, port=port, board=board, family=family)
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

def build_multiple(
    family:str="micropython",
    versions: List[str] = ["v1.19.1"],
    ports: List[str] = ["auto"],
    boards: List[str] = ["GENERIC"],
    production:bool=False,
    clean: bool = False,
    force: bool = False,
) -> List[Dict[str, Any]]:    # sourcery skip: default-mutable-arg
    """
    Build a bunch of stub packages
    """
    db = get_database(CONFIG.publish_path, production=production)
    results = []
    worklist= build_worklist(family, versions, ports, boards)

    for todo in worklist:
        if package := get_package(db, **todo):
            package.build(
                force=force,
                production=production
            )
            results.append(package.status)
        else:
            log.error(f"Failed to create package for {todo}")
    return results


def publish_multiple(
    family:str="micropython",
    versions: List[str] = ["v1.19.1"],
    ports: List[str] = ["auto"],
    boards: List[str] = ["GENERIC"],
    production:bool=False,
    clean: bool = False,
    build: bool = False,
    force: bool = False,
) -> List[Dict[str, Any]]:    # sourcery skip: default-mutable-arg
    """
    Publish a bunch of stub packages
    """
    db = get_database(CONFIG.publish_path, production=production)
    results = []
    worklist= build_worklist(family, versions, ports, boards)

    for todo in worklist:
        if package := get_package(db, **todo):
            package.publish(
                db=db,
                clean=clean,
                force=force,
                build=build,
                production=production
            )
            results.append(package.status)
        else:
            log.error(f"Failed to create package for {todo}")
    return results

def build_worklist(family:str,versions:List[str],ports:List[str], boards:List[str] ):
    """Build a worklist of packages to build or publish"""	
    worklist = []
    worklist += list(firmware_candidates(family=family, versions=versions, pt=COMBO_STUBS))
    worklist = [i for i in worklist if i["board"] != ""]
    if ports != ["auto"]:
        worklist = [i for i in worklist if i["port"] in ports]
    if boards != ["auto"]:
        worklist = [i for i in worklist if i["board"] in boards or i["board"] == "GENERIC"]
    return worklist
