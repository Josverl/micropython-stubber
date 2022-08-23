"""
prepare a set of stub files for publishing to PyPi

required folder structure:

+--stubs
|  +--<any stub folders in repo>
|  +--micropython-v1_18-esp32
|
+--publish
|  +--package_data.jsondb
|  +--package_data_test.jsondb
|  +--template
|     +--pyproject.toml
|     +--README.md
|     +--LICENSE.md
|  +--<folder for each package>
|     +--<package name> double nested to match the folder structure
|  +--<family>-version-<port>-<board>-<type>-stubs
|  +--micropython-v1_18-esp32-stubs
|  +--micropython-v1_18-stm32-stubs
|  +--micropython-v1_19_1-stm32-stubs
|  +-- ...
|


!!Note: anything excluded in .gitignore is not packaged by poetry
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Union

import pytest
from loguru import logger as log
from packaging.version import parse
from pysondb import PysonDB
from stubber.utils.versions import clean_version

from . import stubpacker
from .stubpacker import StubPackage

# replace std log handler with a custom one capped on INFO level
log.remove()
log.add(sys.stderr, level="INFO", backtrace=True, diagnose=True)

ALL_TYPES = ["combo", "doc", "core"]
COMBO_STUBS = ALL_TYPES[0]
DOC_STUBS = ALL_TYPES[1]
CORE_STUBS = ALL_TYPES[2]


def get_database(root_path: Union[Path, str], production: bool = False) -> PysonDB:
    """
    Open the json database at the given path.

    The database should be located in a subfolder `/publish` of the root path.
    The database name is determined by the production flag as `package_data[_test].jsondb`
    """
    root_path = Path(root_path)
    db_path = root_path / f"package_data{'' if production else '_test'}.jsondb"
    return PysonDB(db_path.as_posix())


def package_name(port: str = "", board: str = "", pkg_type=COMBO_STUBS, family="micropython") -> str:
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
    #     log.debug(
    #         f"{x['data']['name']} - {x['data']['mpy_version']} - {x['data']['pkg_version']}"
    #     )
    #     for x in packages
    # ]
    if len(packages) > 0:
        pkg_from_db = packages[-1]["data"]
        log.info(f"Found latest {pkg_name} == {pkg_from_db['pkg_version']}")
        return pkg_from_db
    else:
        return None


def create_package(
    pkg_name: str,
    mpy_version: str,
    *,
    publish_path: Path = stubpacker.PUBLISH_PATH,  # TODO: remove unused parameter
    port: str = "",
    board: str = "",
    family: str = "micropython",
    pkg_type=COMBO_STUBS,
    stub_source="./stubs",  # ?? use stubpacker.STUB_SOURCE, ?? // wrong type
) -> StubPackage:
    """
    create and initialize a package with the correct sources

    """
    package = None
    stub_source = Path(stub_source)
    if pkg_type == COMBO_STUBS:
        assert port != ""
        assert board != ""
        ver_flat = clean_version(mpy_version, flat=True)

        stubs: List[Tuple[str, Path]] = [
            (
                "Firmware stubs",
                stub_source / f"{family}-{ver_flat}-{port}",
            ),
            (
                "Frozen stubs",
                stub_source / f"{family}-{ver_flat}-frozen" / port / board,
            ),
            (
                "Core Stubs",
                stub_source / "cpython_core-pycopy",
            ),
        ]
        package = StubPackage(pkg_name, version=mpy_version, stubs=stubs)
    elif pkg_type == DOC_STUBS:
        # TODO add doc stubs
        ver_flat = clean_version(mpy_version, flat=True)

        stubs: List[Tuple[str, Path]] = [
            (
                "Doc stubs",
                stub_source / f"{family}-{ver_flat}-docstubs",
            ),
        ]
        package = StubPackage(pkg_name, version=mpy_version, stubs=stubs)

    elif pkg_type == CORE_STUBS:
        # TODO add core stubs
        raise NotImplementedError(type)
    else:
        raise NotImplementedError(type)

    return package


# ######################################
# micropython-doc-stubs
# ######################################
# todo : Publish: Integrate doc stubs in publishing loop


def publish_doc_stubs(
    versions: List[str],
    pub_path: Path,
    db: PysonDB,
    family="micropython",
    production=False,  # PyPI or Test-PyPi
    dryrun=False,  # don't publish , dont save to the database
    force=False,  # publish even if no changes
    clean: bool = False,  # clean up afterards
    pkg_type=DOC_STUBS,
    ports=None,
    boards=None,
):
    port = board = ""
    if pkg_type != DOC_STUBS:
        raise NotImplementedError(pkg_type)
    published_packages: List[str] = []
    for mpy_version in versions:
        # package name for firmware package
        # pkg_name = f"micropython-doc-stubs"
        # /////////////////////////
        # dit kan hergebruikt worden

        # package name for firmware package
        pkg_name = package_name(port, board, pkg_type=pkg_type, family=family)
        log.info("=" * 40)

        package_info = get_package_info(
            db,
            pub_path,
            pkg_name=pkg_name,
            mpy_version=mpy_version,
        )
        if package_info:
            # create package from the information retrieved from the database
            package = stubpacker.StubPackage(pkg_name, version=mpy_version, json_data=package_info)

        else:
            log.warning(f"No package found for {pkg_name}")
            package = create_package(
                pkg_name,
                mpy_version,
                port=port,
                board=board,
                family=family,
                pkg_type=pkg_type,
            )

        # check if the sources exist
        OK = True
        for (name, path) in package.stub_sources:
            if not path.exists():
                log.warning(f"{pkg_name}: source {name} does not exist: {path}")
                OK = False
        if not OK:
            log.warning(f"{pkg_name}: skipping as one or more source stub folders are missing")

            package._publish = False
            continue

        package.update_package_files()
        package.update_included_stubs()
        package.check()

        # If there are changes to the package, then publish it
        if not (package.is_changed() or force):
            log.info(f"No changes to package : {package.package_name} {package.pkg_version}")
        else:
            if not force:
                log.info(
                    f"Found changes to package : {package.package_name} {package.pkg_version} {package.hash} != {package.create_hash()}"
                )
            ## TODO: get last published version.postXXX from PyPI and update version if different
            package.bump()
            package.hash = package.create_hash()
            log.debug(f"New hash: {package.package_name} {package.pkg_version} {package.hash}")
            if dryrun:
                log.warning("Dryrun: Updated package is NOT published.")
            else:
                result = package.build()
                if not result:
                    log.warning(f"{pkg_name}: skipping as build failed")
                    continue
                result = package.publish(production=production)
                if not result:
                    log.warning(f"{pkg_name}: Publish failed for {package.pkg_version}")
                    continue
                published_packages.append(package.package_name)
                db.add(package.to_json())
                db.commit()
                # TODO: push to github
                # git add tests\publish\data\package_data_test.jsondb
                # git commit -m "Publish micropython-esp32-stubs (1.18.post24)"
                # git push
                # add tag ?

        if clean:
            package.clean()
    return published_packages


def publish_combo_stubs(
    versions: List[str],
    ports: List[str],
    boards: List[str],
    db: PysonDB,
    pub_path: Path,
    pkg_type=COMBO_STUBS,
    family: str = "micropython",
    production=False,  # PyPI or Test-PyPi
    dryrun=False,  # don't publish , dont save to the database
    force=False,  # publish even if no changes
    clean: bool = False,  # clean up afterards
):
    if pkg_type != COMBO_STUBS:
        raise NotImplementedError(pkg_type)

    published_packages: List[str] = []
    for mpy_version in versions:
        for port in ports:

            # Firmware Stubber MUST report "stm32" for a pyboard
            for board in boards:

                # /////////////////////////
                # dit kan hergebruikt worden

                # package name for firmware package
                pkg_name = package_name(port, board, pkg_type=pkg_type, family=family)
                log.info("=" * 40)

                package_info = get_package_info(
                    db,
                    pub_path,
                    pkg_name=pkg_name,
                    mpy_version=mpy_version,
                )
                if package_info:
                    # create package from the information retrieved from the database
                    package = stubpacker.StubPackage(pkg_name, version=mpy_version, json_data=package_info)

                else:
                    log.warning(f"No package found for {pkg_name}")
                    package = create_package(
                        pkg_name,
                        mpy_version,
                        port=port,
                        board=board,
                        family=family,
                        pkg_type=pkg_type,
                    )
                    continue

                # check if the sources exist
                OK = True
                for (name, path) in package.stub_sources:
                    if not path.exists():
                        log.warning(f"{pkg_name}: source {name} does not exist: {path}")
                        OK = False
                if not OK:
                    log.warning(f"{pkg_name}: skipping as one or more source stub folders are missing")

                    package._publish = False
                    continue

                package.update_package_files()
                package.update_included_stubs()
                package.check()

                # If there are changes to the package, then publish it
                if not (package.is_changed() or force):
                    log.info(f"No changes to package : {package.package_name} {package.pkg_version}")
                else:
                    if not force:
                        log.info(
                            f"Found changes to package : {package.package_name} {package.pkg_version} {package.hash} != {package.create_hash()}"
                        )
                    ## TODO: get last published version.postXXX from PyPI and update version if different
                    package.bump()
                    package.hash = package.create_hash()
                    log.debug(f"New hash: {package.package_name} {package.pkg_version} {package.hash}")
                    if dryrun:
                        log.warning("Dryrun: Updated package is NOT published.")
                    else:
                        result = package.build()
                        if not result:
                            log.warning(f"{pkg_name}: skipping as build failed")
                            continue
                        result = package.publish(production=production)
                        if not result:
                            log.warning(f"{pkg_name}: Publish failed for {package.pkg_version}")
                            continue
                        published_packages.append(package.package_name)
                        db.add(package.to_json())
                        db.commit()
                        # TODO: push to github
                        # git add tests\publish\data\package_data_test.jsondb
                        # git commit -m "Publish micropython-esp32-stubs (1.18.post24)"
                        # git push
                        # add tag ?

                if clean:
                    package.clean()
    return published_packages
