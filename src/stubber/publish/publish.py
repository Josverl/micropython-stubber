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

from itertools import chain
from typing import Any, Dict, List, Union

from loguru import logger as log
from pysondb import PysonDB
from stubber.publish.candidates import frozen_candidates
from stubber.publish.database import get_database
from stubber.publish.package import StubSource, create_package, get_package_info, package_name
from stubber.publish.pypi import Version, get_pypy_versions
from stubber.publish.stubpacker import StubPackage
from stubber.utils.config import CONFIG
from stubber.utils.versions import clean_version


# ######################################
# micropython-doc-stubs
# ######################################
# todo : Publish: Integrate doc stubs in publishing loop
def publish(
    *,
    db: PysonDB,
    pkg_type,
    version: str,
    family="micropython",
    production,  # PyPI or Test-PyPi
    dryrun=False,  # don't publish , dont save to the database
    force=False,  # publish even if no changes
    clean: bool = False,  # clean up afterards
    port: str = "",
    board: str = "",
) -> Dict[str, Any]:
    """
    Publish a package to PyPi
    look up the previous package version in the dabase, and only publish if there are changes to the package
    - change determied by hash across all files

    """
    # semver, no prefix
    version = clean_version(version, drop_v=True, flat=False)
    # package name for firmware package
    pkg_name = package_name(pkg_type=pkg_type, port=port, board=board, family=family)
    status: Dict[str, Any] = {"result": "-", "name": pkg_name, "version": version, "error": None}
    log.debug("=" * 40)

    package_info = get_package_info(
        db,
        CONFIG.publish_path,
        pkg_name=pkg_name,
        mpy_version=version,
    )
    if package_info:
        # create package from the information retrieved from the database
        package = StubPackage(pkg_name, version=version, json_data=package_info)

    else:
        log.debug(f"No package found for {pkg_name} in database, creating new package")
        package = create_package(
            pkg_name,
            mpy_version=version,
            port=port,
            board=board,
            family=family,
            pkg_type=pkg_type,
        )
    log.info(f"Processing {package.package_path.name}")
    log.trace(f"{package.package_path.as_posix()}")
    status["version"] = package.pkg_version
    # check if the sources exist
    ok = True
    for (name, path) in package.stub_sources:
        if not (CONFIG.stub_path / path).exists():
            msg = f"{pkg_name}: source '{name}' not found: {CONFIG.stub_path / path}"
            if not name == StubSource.FROZEN:
                log.warning(msg)
                log.warning(msg)
                status["error"] = msg
                ok = False
            else:
                # not a blocking issue if there are no frozen stubs, perhaps this port/board does not have any
                log.warning(msg)
    if not ok:
        log.warning(f"{pkg_name}: skipping as one or more source stub folders are missing")
        package._publish = False
        # TODO Save ?
        return status
    try:

        package.update_package_files()
        package.update_included_stubs()
        package.check()
    except Exception as e:  # pragma: no cover
        log.error(f"{pkg_name}: {e}")
        status["error"] = str(e)
        return status

    # If there are changes to the package, then publish it
    if not (package.is_changed() or force):
        log.debug(f"No changes to package : {package.package_name} {package.pkg_version}")
    else:
        if not force:  # pragma: no cover
            log.info(f"Found changes to package : {package.package_name} {package.pkg_version}")
            log.debug(f"Old hash {package.hash} != New hash {package.create_hash()}")
        # if not dryrun:
        # only bump version if we are going to publish
        # get last published version.postXXX from PyPI and update version if different
        # try to get version from PyPi and increase past that
        old_ver = package.pkg_version
        pypi_versions = get_pypy_versions(package.package_name, production=production, base=Version(package.pkg_version))
        if pypi_versions:
            package.pkg_version = str(pypi_versions[-1])
        # to get the next version
        new_ver = package.bump()

        log.debug(f"{pkg_name}: bump version for {old_ver} to {new_ver} {production}")
        # Update hashes
        package.update_hashes()
        package.write_package_json()

        status["version"] = package.pkg_version

        log.trace(f"New hash: {package.package_name} {package.pkg_version} {package.hash}")
        result = package.build()
        if not result:
            log.warning(f"{pkg_name}: skipping as build failed")
            status["error"] = "Build failed"
            return status

        if dryrun:  # pragma: no cover
            log.warning("Dryrun: Updated package is NOT published.")
            status["result"] = "DryRun successful"
        else:
            result = package.publish(production=production)
            if not result:
                log.warning(f"{pkg_name}: Publish failed for {package.pkg_version}")
                status["error"] = "Publish failed"
                return status
            status["result"] = "Published"
            db.add(package.to_dict())
            db.commit()

    if clean:
        package.clean()
    return status


def publish_one(
    family="micropython",
    versions: Union[str, List[str]] = "v1.18",
    ports: Union[str, List[str]] = "auto",
    boards: Union[str, List[str]] = "GENERIC",
    frozen: bool = False,
    production=False,
    dryrun: bool = False,
    clean: bool = False,
    force: bool = False,
):
    "Publish a bunch of stub packages"
    db = get_database(CONFIG.publish_path, production=production)
    l = list(frozen_candidates(family=family, versions=versions, ports=ports, boards=boards))
    result = None
    if len(l) > 0:
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
    family="micropython",
    versions: Union[str, List[str]] = ["v1.18", "v1.19"],
    ports: Union[str, List[str]] = "auto",
    boards: Union[str, List[str]] = "GENERIC",
    frozen: bool = False,
    production=False,
    dryrun: bool = False,
    clean: bool = False,
    force: bool = False,
):
    "Publish a bunch of stub packages"
    db = get_database(CONFIG.publish_path, production=production)

    worklist = []
    results = []
    if frozen:
        worklist += list(
            chain(
                frozen_candidates(family=family, versions=versions, ports=ports, boards=boards),
                # frozen_candidates(family="micropython", versions="v1.19.1", ports="auto", boards="auto"),
            )
        )
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
