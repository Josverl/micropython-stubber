"""
prepare a set of stub files for publishing to PyPi

!!Note: anything excluded in .gitignore is not packaged by poetry
"""

from typing import Any, Dict, List, Optional, Union

from mpflash.logger import log
from mpflash.versions import V_PREVIEW

from stubber.publish.candidates import board_candidates, best_matching_port, firmware_candidates, filter_list, is_auto
from stubber.publish.database import get_database
from stubber.publish.defaults import DEFAULT_L, GENERIC_L, GENERIC_U
from stubber.publish.enums import PackageType
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
    package_type: Union[PackageType, str] = CONFIG.package_type,
) -> List[Dict[str, Any]]:  # sourcery skip: default-mutable-arg
    """
    Build a bunch of stub packages
    """
    # default parameter values
    versions = versions or [V_PREVIEW]
    ports = ports or ["all"]
    boards = boards or [GENERIC_U]

    db_conn = get_database(CONFIG.publish_path, production=production)
    results: List[Dict[str, Any]] = []
    worklist = build_worklist(family, versions, ports, boards)
    if len(worklist) == 0:
        log.error("Could not find any packages that can be build.")
        return results
    log.info(f"checking {len(worklist)} possible board candidates")

    for todo in worklist:
        if package := get_package(db_conn, **todo, package_type=package_type):
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
    package_type: Union[PackageType, str] = CONFIG.package_type,
) -> List[Dict[str, Any]]:  # sourcery skip: default-mutable-arg
    """
    Publish a bunch of stub packages
    """
    # default parameter values
    versions = versions or [V_PREVIEW]
    ports = ports or ["all"]
    boards = boards or [GENERIC_U]

    db_conn = get_database(CONFIG.publish_path, production=production)
    results = []
    worklist = build_worklist(family, versions, ports, boards)

    if len(worklist) == 0:
        log.error("Could not find any packages that can be published.")
        return results

    for todo in worklist:
        if package := get_package(db_conn, **todo, package_type=package_type):
            package.publish_distribution_ifchanged(
                db_conn=db_conn,
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

    # Correct any out-of-tree port names (e.g. 'nrf52' -> 'nrf') before looking up boards,
    # so that both the source-tree lookup and the firmware-stub fallback use the real port.
    if ports and not is_auto(ports):
        corrected_ports = []
        for p in ports:
            matched = best_matching_port(p, family=family)
            if matched and matched != p:
                log.warning(f"Port '{p}' is not a known MicroPython port; using best matching port '{matched}'")
            corrected_ports.append(matched or p)
        ports = corrected_ports

    # get all the candidates from the micropython source tree
    worklist = list(board_candidates(family=family, versions=versions))
    worklist = filter_list(worklist, ports, boards)

    # Check which requested boards were not found
    requested_boards = boards if boards else [GENERIC_U]
    requested_boards = [b for b in requested_boards if b.lower() not in ["auto", "all", "*"]]

    for b in requested_boards:
        board_check = GENERIC_L if b.lower() == DEFAULT_L else b.lower()
        if not any(i for i in worklist if i["board"].lower() == board_check):
            log.warning(f"Could not find any package candidate for board {b}")

            # Fallback: Look for firmware stubs that may have been generated for this board
            # This handles out-of-tree custom boards
            firmware_worklist = list(firmware_candidates(family=family, versions=versions, ports=ports, boards=[b]))
            if firmware_worklist:
                log.info(f"Found existing firmware stubs for custom board {b}, using those for build")
                worklist.extend(firmware_worklist)

    return worklist
