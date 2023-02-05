"""
prepare a set of stub files for publishing to PyPi

!!Note: anything excluded in .gitignore is not packaged by poetry
"""
from typing import Any, Dict, List
from loguru import logger as log

from stubber.publish.candidates import firmware_candidates, is_auto
from stubber.publish.database import get_database
from stubber.publish.enums import COMBO_STUBS
from stubber.publish.package import create_package, get_package, get_package_info, package_name
from stubber.publish.stubpacker import StubPackage
from stubber.utils.config import CONFIG

from pysondb import PysonDB


def build_multiple(
    family: str = "micropython",
    versions: List[str] = ["v1.19.1"],
    ports: List[str] = ["auto"],
    boards: List[str] = ["GENERIC"],
    production: bool = False,
    clean: bool = False,
    force: bool = False,
) -> List[Dict[str, Any]]:  # sourcery skip: default-mutable-arg
    """
    Build a bunch of stub packages
    """
    db = get_database(CONFIG.publish_path, production=production)
    results = []
    worklist = build_worklist(family, versions, ports, boards)

    for todo in worklist:
        if package := get_package(db, **todo):
            package.build(force=force, production=production)
            results.append(package.status)
        else:
            log.error(f"Failed to create package for {todo}")
    return results


def publish_multiple(
    family: str = "micropython",
    versions: List[str] = ["v1.19.1"],
    ports: List[str] = ["auto"],
    boards: List[str] = ["GENERIC"],
    production: bool = False,
    clean: bool = False,
    build: bool = False,
    force: bool = False,
) -> List[Dict[str, Any]]:  # sourcery skip: default-mutable-arg
    """
    Publish a bunch of stub packages
    """
    db = get_database(CONFIG.publish_path, production=production)
    results = []
    worklist = build_worklist(family, versions, ports, boards)

    for todo in worklist:
        if package := get_package(db, **todo):
            package.publish(db=db, clean=clean, force=force, build=build, production=production)
            results.append(package.status)
        else:
            log.error(f"Failed to create package for {todo}")
    return results


def build_worklist(family: str, versions: List[str], ports: List[str], boards: List[str]):
    """Build a worklist of packages to build or publish, and filter to only the requested ports and boards"""
    if isinstance(versions, str):
        versions = [versions]
    if isinstance(ports, str):
        ports = [ports]
    if isinstance(boards, str):
        boards = [boards]
    if family != "micropython":
        return []
    # get all the candidates
    worklist = list(firmware_candidates(family=family, versions=versions, pt=COMBO_STUBS))
    worklist = [i for i in worklist if i["board"] != ""]
    # then filter down to the ones we want
    if not is_auto(ports):
        ports_ = [i.upper() for i in ports]
        worklist = [i for i in worklist if i["port"].upper() in ports_]
    if not is_auto(boards):
        boards_ = [i.upper() for i in boards]
        worklist = [i for i in worklist if i["board"].upper() in boards_]
    return worklist
