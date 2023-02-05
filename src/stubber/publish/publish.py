"""
prepare a set of stub files for publishing to PyPi

required folder structure:
NOTE: stubs and publish paths can be located in different locations and repositories

+--stubs                                                               - [config.stubs_path]
|  +--<any stub folders in repo>
|  +--micropython-v1_18-esp32
+--publish                                                             - [config.publish_path]
|  +--package_data.jsondb
|  +--package_data_test.jsondb
|  +--template                                                         - [config.template_path]
|     +--pyproject.toml
|     +--README.md
|     +--LICENSE.md
|  +--<folder for each package>
|     +--<package name> double nested to match the folder structure
|  +--<family>-<port>-<board>-<type>-stubs-<version>
|  +--micropython-esp32-stubs-v1_18
|  +--micropython-stm32-stubs-v1_18
|  +--micropython-stm32-stubs-v1_19_1
|  +-- ...
|


!!Note: anything excluded in .gitignore is not packaged by poetry
"""

import shutil
from typing import Any, Dict, List, Optional, Tuple, Union

from loguru import logger as log
from pysondb import PysonDB

from stubber.publish.bump import bump_postrelease
from stubber.publish.candidates import firmware_candidates, frozen_candidates
from stubber.publish.database import get_database
from stubber.publish.enums import COMBO_STUBS
from stubber.publish.package import (StubSource, create_package,
                                     get_package_info, package_name)
from stubber.publish.pypi import Version, get_pypy_versions
from stubber.publish.stubpacker import StubPackage
from stubber.utils.config import CONFIG
from stubber.utils.versions import clean_version

# ######################################
# micropython-doc-stubs
# ######################################

from typing import NewType

Status = NewType('Status', Dict[str, Union[ str, None]])

def publish(
    *,
    db: PysonDB,
    pkg_type,
    version: str,
    family:str="micropython",
    production:bool,  # PyPI or Test-PyPi
    dryrun=False,  # don't publish , don't save to the database
    force=False,  # publish even if no changes
    clean: bool = False,  # clean up afterwards
    port: str = "",
    board: str = "",
) -> Status:    # sourcery skip: default-mutable-arg, require-parameter-annotation
    """
    Publish a package to PyPi
    look up the previous package version in the dabase, and only publish if there are changes to the package
    - change determied by hash across all files

    Build
        - update package files
        - build the wheels and sdist
    Publish 
        - publish to PyPi
        - update database with new hash    
    """
    version = clean_version(version, drop_v=True, flat=False)
    # package name for firmware package
    pkg_name = package_name(pkg_type=pkg_type, port=port, board=board, family=family)
    status: Status = Status({"result": "-", "name": pkg_name, "version": version, "error": None})
    log.debug("=" * 40)
    # #####################################################
    # Build the package
    package, ok, status = update_package(db, pkg_type, version, family, port, board, pkg_name, status)
    if not ok:
        return failed_build(pkg_name, status)
    # If there are changes to the package, then publish it
    if package.is_changed():
        build_ok = build_dist(production, force, pkg_name, status, package)
        if not build_ok:
            return failed_build(pkg_name, status)

    # #####################################################
    # Publish the package
    if dryrun:  # pragma: no cover
        log.warning("Dryrun: Updated package is NOT published.")
        status["result"] = "DryRun successful"
        if clean:
            package.clean()
        return status
    status = publish_package(db, package, production, force, pkg_name, status)
    if clean:
        package.clean()
    return status

def publish_package(db:PysonDB ,package:StubPackage, production:bool,force:bool, pkg_name:str, status:Status) -> Status:
    """Publish the package to PyPi, Test-PyPi or Github"""
    if package.is_changed():
        if force:
            force_package_update(package, production, pkg_name, status)
        if package.mpy_version == "latest":
            log.warning("version: `latest` package will only be available on Github, and not published to PyPi.")
            status["result"] = "Published to GitHub"
        else:
            build_ok = package.publish(production=production)
            if not build_ok:
                return failed_publish(pkg_name, package, status)
            status["result"] = "Published to PyPi" if production else "Published to Test-PyPi"
            db.add(package.to_dict())
            db.commit()
    elif force:
        force_package_update(package, production, pkg_name, status)
        if package.mpy_version == "latest":
            log.warning("version: `latest` package will only be available on Github, and not published to PyPi.")
            status["result"] = "Published to GitHub"
        else:
            build_ok = package.publish(production=production)
            if not build_ok:
                return failed_publish(pkg_name, package, status)
            status["result"] = "Published to PyPi" if production else "Published to Test-PyPi"
            db.add(package.to_dict())
            db.commit()
    else:
        log.debug(f"No changes to package : {package.package_name} {package.pkg_version}")
    return status

def force_package_update(package:StubPackage, production:bool, pkg_name:str, status:Status) -> None:
    """Force an update of the package version and hashes"""	
    log.warning("Force: Update of package")
    old_ver = package.pkg_version
    if package.mpy_version == "latest":
        new_ver = prerelease_package_version(package, production)
        package.pkg_version = new_ver
    else:
        new_ver = next_package_version(package, production)
    # to get the next version
    log.debug(f"{pkg_name}: bump version for {old_ver} to {new_ver} {production}")
    # Update hashes
    package.update_hashes()
    package.write_package_json()
    status["version"] = package.pkg_version

def build_dist(production:bool, force:bool, pkg_name:str, status:Status, package: StubPackage)-> bool:
    if not force:  # pragma: no cover
        log.info(f"Found changes to package sources: {package.package_name} {package.pkg_version}")
        log.debug(f"Old hash {package.hash} != New hash {package.create_hash()}")
        # if not dryrun:
        # only bump version if we are going to publish
        # get last published version.postXXX from PyPI and update version if different
        # try to get version from PyPi and increase past that
    old_ver = package.pkg_version
    status["version"] = package.pkg_version = updated_package_version(production, package)
        # to get the next version
    log.debug(f"{pkg_name}: bump version for {old_ver} to {package.pkg_version } {production}")
    # Update hashes
    package.update_hashes()
    package.write_package_json()
    log.trace(f"New hash: {package.package_name} {package.pkg_version} {package.hash}")
    return package.build()

def update_package(db:PysonDB, pkg_type, version, family:str, port:str, board:str, pkg_name:str, status:Status) -> Tuple[StubPackage, bool, Status]:
    """Update the package files and check that the sources are available"""
    package = get_package(db, pkg_type, version, family, port, board, pkg_name)
    log.info(f"Processing {package.package_path.name}")
    log.trace(f"{package.package_path.as_posix()}")
    status["version"] = package.pkg_version
    # check if the sources exist
    ok = package_sources_available(pkg_name, status, package)
    if not ok:
        log.warning(f"{pkg_name}: skipping as one or more source stub folders are missing")
        shutil.rmtree(package.package_path.as_posix())
        package._publish = False  # type: ignore
        return package, ok, status
    try:
        package.update_package_files()
        package.update_included_stubs()
        package.check()
    except Exception as e:  # pragma: no cover
        log.error(f"{pkg_name}: {e}")
        status["error"] = str(e)
        ok = False
        return package, ok, status
    return package, ok, status

def updated_package_version(production, package) -> str:
    """Get the next version for the package"""
    return (
        prerelease_package_version(package, production)
        if package.mpy_version == "latest"
        else next_package_version(package, production)
    )

def package_sources_available(pkg_name, status, package) -> bool:
    """
    Check if (all) the packages sources exist.
    """
    ok = True
    for (name, path) in package.stub_sources:
        if not (CONFIG.stub_path / path).exists():
            # todo: below is a workaround for different types, but where is the source of this difference coming from?
            msg = f"{pkg_name}: source '{name._value_}' not found: {CONFIG.stub_path / path}" if isinstance(name, StubSource) else f"{pkg_name}: source '{name}' not found: {CONFIG.stub_path / path}"
            if name != StubSource.FROZEN:
                log.warning(msg)
                status["error"] = msg
                ok = False
            else:
                # not a blocking issue if there are no frozen stubs, perhaps this port/board does not have any
                log.warning(msg)
    return ok

def get_package(db, pkg_type, version, family, port, board, pkg_name) -> StubPackage:
    """Get the package from the database or create a new one if it does not exist."""
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


def failed_publish(pkg_name:str, package, status:Status) -> Status:
    """Publish failed, so return the status."""
    log.warning(f"{pkg_name}: Publish failed for {package.pkg_version}")
    status["error"] = "Publish failed"
    return status


def failed_build(pkg_name:str, status:Status) -> Status:
    """Build failed, so return the status."""
    log.warning(f"{pkg_name}: skipping as build failed")
    status["error"] = "Build failed"
    return status

def prerelease_package_version(package:StubPackage, prod:bool=False)->str:
    """Get the next prerelease version for the package."""
    base = Version("1.20") # TODO hardcoded version - should be the next minor version after the last release
    rc = 744  # FIXME: #307 hardcoded prerelease version - should be based on the git commit count
    return str(bump_postrelease(base, rc=rc))  

def next_package_version(package:StubPackage, prod:bool=False)->str:
    """Get the next version for the package."""
    base = Version(package.pkg_version)
    if pypi_versions := get_pypy_versions(package.package_name, production=prod, base=base):
        package.pkg_version = str(pypi_versions[-1])
    return package.bump()


def publish_one(
    family:str="micropython",
    versions: Union[str, List[str]] = "v1.18",
    ports: Union[str, List[str]] = "auto",
    boards: Union[str, List[str]] = "GENERIC",
    frozen: bool = False,
    production:bool=False,
    dryrun: bool = False,
    clean: bool = False,
    force: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Publish a bunch of stub packages of the same version
    """
    db = get_database(CONFIG.publish_path, production=production)
    l = list(frozen_candidates(family=family, versions=versions, ports=ports, boards=boards))
    result = None
    if l:
        todo = l[0]
        result = publish(
            db=db,
            dryrun=dryrun,
            clean=clean,
            force=force,
            production=production,
            **todo,
        )
    return result


def publish_multiple(
    family:str="micropython",
    versions: List[str] = ["v1.18", "v1.19.1"],
    ports: List[str] = ["auto"],
    boards: List[str] = ["GENERIC"],
    frozen: bool = False,
    production:bool=False,
    dryrun: bool = False,
    clean: bool = False,
    force: bool = False,
) -> List[Dict[str, Any]]:  # sourcery skip: default-mutable-arg
    """
    Publish a bunch of stub packages
    """
    db = get_database(CONFIG.publish_path, production=production)

    worklist = []
    results = []

    worklist += list(firmware_candidates(family=family, versions=versions, pt=COMBO_STUBS))
    # if frozen:
    #     worklist += list(
    #         chain(
    #             frozen_candidates(family=family, versions=versions, ports=ports, boards=boards),
    #             # frozen_candidates(family="micropython", versions="v1.19.1", ports="auto", boards="auto"),
    #         )
    #     )
    # remove unneeded extras from worklist
    worklist = [i for i in worklist if i["board"] != ""]
    if ports != ["auto"]:
        worklist = [i for i in worklist if i["port"] in ports]
    if boards != ["auto"]:
        worklist = [i for i in worklist if i["board"] in boards or i["board"] == "GENERIC"]

    for todo in worklist:

        result = publish(
            db=db,
            dryrun=dryrun,
            clean=clean,
            force=force,
            production=production,
            **todo,
        )
        results.append(result)

    return results
