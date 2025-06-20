"""
prepare a set of stub files for publishing to PyPi

"""

import sqlite3
import sys
from pathlib import Path
from typing import Dict, Union

from mpflash.logger import log
from mpflash.versions import clean_version

from stubber.publish.defaults import GENERIC, GENERIC_L, default_board
from stubber.publish.enums import StubSource
from stubber.publish.stubpackage import StubPackage, StubSources
from stubber.utils.config import CONFIG

# replace std log handler with a custom one capped on INFO level
log.remove()
log.add(sys.stderr, level="INFO", backtrace=True, diagnose=True)


def package_name(*, port: str = "", board: str = "", family: str = "micropython", **kwargs) -> str:
    "generate a package name for the given package type"
    # # {family}-{port}[-{board}[-{variant}]]-stubs
    name = f"{family}-{port}-{board}-stubs".lower()
    name = name.replace("-generic-stubs", "-stubs")
    # Use explicit generic_ names for the stubs
    # name = name.replace("-generic_", "-")  # @GENERIC Prefix
    return name


def get_package(
    db_conn: sqlite3.Connection,
    *,
    version: str,
    port: str,
    board: str = GENERIC_L,
    family: str = "micropython",
) -> StubPackage:
    """Get the package from the database or create a new one if it does not exist."""
    pkg_name = package_name(port=port, board=board, family=family)
    version = clean_version(version, drop_v=True)
    if package_info := get_package_info(
        db_conn,
        CONFIG.publish_path,
        pkg_name=pkg_name,
        mpy_version=version,
    ):
        # create package from the information retrieved from the database
        p_db =  StubPackage(
            pkg_name,
            port,
            board=board,
            version=version,
            json_data=package_info,
        )
        # TODO @Josverl: Check or update stub_sources in len < 3
        EXPECTED_STUBS = 3
        if len(p_db.stub_sources) < EXPECTED_STUBS:
            log.warning(f"Package {pkg_name} has less than 3 stub sources, updating...")
            stub_sources = combo_sources(family, port, board, clean_version(p_db.mpy_version, flat=True))
            if len(stub_sources) >= EXPECTED_STUBS:
                p_db.stub_sources = stub_sources
                p_db.update_sources()
                log.info(f"Updated stub sources for {pkg_name} to {p_db.stub_sources}")
        return p_db

    log.debug(f"No package found for {pkg_name} in database, creating new package")
    return create_package(
        pkg_name,
        mpy_version=version,
        port=port,
        board=board,
        family=family,
    )


def get_package_info(
    db_conn: sqlite3.Connection,
    pub_path: Path,
    *,
    pkg_name: str,
    mpy_version: str,
) -> Union[Dict, None]:
    """
    get a package's record from the json db if it can be found
    matches on the package name and version
        pkg_name: package name (micropython-esp32-stubs)
        mpy_version: micropython/firmware version (1.18)
    """
    # find in the database

    cursor = db_conn.cursor()
    cursor.execute(
        """
        SELECT * FROM packages 
        WHERE name = ? AND mpy_version LIKE ?
        ORDER BY pkg_version DESC
    """,
        (pkg_name, f"{mpy_version}%"),
    )
    packages = [dict(row) for row in cursor.fetchall()]

    if packages:
        pkg_from_db = packages[0]

        log.debug(f"Found latest {pkg_name} == {pkg_from_db['pkg_version']}")
        return pkg_from_db
    return None


def create_package(
    pkg_name: str,
    mpy_version: str,
    *,
    port: str,
    board: str = "",
    family: str = "micropython",
    # pkg_type: str = COMBO_STUBS,
) -> StubPackage:  # sourcery skip: merge-duplicate-blocks, remove-redundant-if
    """
    create and initialize a package with the correct sources
    """
    ver_flat = clean_version(mpy_version, flat=True)
    stub_sources: StubSources = []
    # if pkg_type != COMBO_STUBS:
    #     raise ValueError("Not Supported")

    assert port != "", "port must be specified for combo stubs"
    stub_sources = combo_sources(family, port, board, ver_flat)
    return StubPackage(pkg_name, port=port, board=board, version=mpy_version, stub_sources=stub_sources)


def combo_sources(family: str, port: str, board: str, ver_flat: str) -> StubSources:
    """
    Build a source set for combo stubs
    """
    # Use lower case for paths to avoid case sensitive issues
    port = port.lower()
    # BOARD in the micropython repo is always uppercase by convention (GENERIC)
    # but MUST  be used in lowercase in the stubs repo
    board_l = board.lower() if board else GENERIC_L
    board_u = board_l.upper()
    board_l = board_l.replace("generic_", "")  # @GENERIC Prefix

    # StubSource.FIRMWARE,
    # Path(f"{family}-{ver_flat}-{port}"),
    # TODO: look for the most specific firmware stub folder that is available ?
    # is it possible to prefer micropython-nrf-microbit-stubs over micropython-nrf-stubs
    # that would also require the port - board - variant to be discoverable runtime

    if board_l in GENERIC:
        merged_path = Path(f"{family}-{ver_flat}-{port}-merged")
        if not merged_path.exists():
            board = default_board(port, ver_flat)
            board_l = board.lower()
            board_u = board
            merged_path = Path(f"{family}-{ver_flat}-{port}-{board}-merged")
    else:
        merged_path = Path(f"{family}-{ver_flat}-{port}-{board}-merged")

    # BOARD in source frozen path needs to be UPPERCASE
    frozen_path = Path(f"{family}-{ver_flat}-frozen") / port / board_u.upper()
    # TODO : Add version to core stubs
    core_path = Path(f"{family}-core")

    return [
        (StubSource.MERGED, merged_path),
        (StubSource.FROZEN, frozen_path),
        (StubSource.CORE, core_path),
    ]
