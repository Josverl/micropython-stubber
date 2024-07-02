"""
prepare a set of stub files for publishing to PyPi

!!Note: anything excluded in .gitignore is not packaged by poetry
"""

from typing import Any, Dict, List, Optional, Union

from mpflash.logger import log

from mpflash.versions import V_PREVIEW
from stubber.publish.candidates import board_candidates, filter_list
from stubber.publish.database import get_database
from stubber.publish.defaults import GENERIC_U
from stubber.publish.package import get_package
from stubber.utils.config import CONFIG


def build_multiple(
    family: str = "micropython",
    versions: Optional[List[str]] = None,
    ports: Optional[List[str]] = None,
    boards: Optional[List[str]] = None,
    production: bool = False,
    clean: bool = False,
    force: bool = False,
) -> List[Dict[str, Any]]:  # sourcery skip: default-mutable-arg
    """
    Build a bunch of stub packages
    """
    # default parameter values
    versions = versions or [V_PREVIEW]
    ports = ports or ["all"]
    boards = boards or [GENERIC_U]

    db = get_database(CONFIG.publish_path, production=production)
    results: List[Dict[str, Any]] = []
    worklist = build_worklist(family, versions, ports, boards)
    if len(worklist) == 0:
        log.error("Could not find any packages that can be build.")
        return results
    log.info(f"checking {len(worklist)} possible board candidates")

    for todo in worklist:
        if package := get_package(db, **todo):
            package.build_distribution(force=force, production=production)
            results.append(package.status)
        else:
            log.error(f"Failed to create package for {todo}")
    return results


def publish_multiple(
    family: str = "micropython",
    versions: Optional[List[str]] = None,
    ports: Optional[List[str]] = None,
    boards: Optional[List[str]] = None,
    production: bool = False,
    clean: bool = False,
    build: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> List[Dict[str, Any]]:  # sourcery skip: default-mutable-arg
    """
    Publish a bunch of stub packages
    """
    # default parameter values
    versions = versions or [V_PREVIEW]
    ports = ports or ["all"]
    boards = boards or [GENERIC_U]

    db = get_database(CONFIG.publish_path, production=production)
    results = []
    worklist = build_worklist(family, versions, ports, boards)

    if len(worklist) == 0:
        log.error("Could not find any packages than can be published.")
        return results

    for todo in worklist:
        if package := get_package(db, **todo):
            package.publish_distribution_ifchanged(
                db=db,
                clean=clean,
                force=force,
                build=build,
                production=production,
                dry_run=dry_run,
            )
            results.append(package.status)
        else:
            log.error(f"Failed to create package for {todo}")
    return results


def build_worklist(
    family: str,
    versions: Union[List[str], str],
    ports: Union[List[str], str],
    boards: Union[List[str], str],
):
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
    worklist = list(board_candidates(family=family, versions=versions))
    worklist = filter_list(worklist, ports, boards)

    for b in boards:
        if b == "auto":
            continue
        if not any(i for i in worklist if i["board"].lower() == b.lower()):
            log.warning(f"Could not find any package candidate for board {b}")
    return worklist
