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

import sys
from itertools import chain
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from loguru import logger as log
from packaging.version import parse
from pysondb import PysonDB
from stubber.publish.candidates import frozen_candidates
from stubber.publish.database import get_database
from stubber.utils.config import CONFIG
from stubber.utils.versions import clean_version

from . import stubpacker
from .package import COMBO_STUBS, CORE_STUBS, DOC_STUBS, create_package, get_package_info, package_name
from .stubpacker import StubPackage


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
    production=False,  # PyPI or Test-PyPi
    dryrun=False,  # don't publish , dont save to the database
    force=False,  # publish even if no changes
    clean: bool = False,  # clean up afterards
    port: str = "",
    board: str = "",
):
    """
    Publish a package to PyPi
    look up the previous package version in the dabase, and only publish if there are changes to the package
    - change determied by hash across all files

    """
    # semver, no prefix
    version = clean_version(version, drop_v=True, flat=False)

    # package name for firmware package
    pkg_name = package_name(pkg_type=pkg_type, port=port, board=board, family=family)
    log.info("=" * 40)

    package_info = get_package_info(
        db,
        CONFIG.publish_path,
        pkg_name=pkg_name,
        mpy_version=version,
    )
    if package_info:
        # create package from the information retrieved from the database
        package = stubpacker.StubPackage(pkg_name, version=version, json_data=package_info)

    else:
        log.warning(f"No package found for {pkg_name}")
        package = create_package(
            pkg_name,
            mpy_version=version,
            port=port,
            board=board,
            family=family,
            pkg_type=pkg_type,
        )

    # check if the sources exist
    OK = True
    for (name, path) in package.stub_sources:
        if not (CONFIG.stub_path / path).exists():
            log.warning(f"{pkg_name}: source {name} does not exist: {CONFIG.stub_path / path}")
            OK = False
    if not OK:
        log.warning(f"{pkg_name}: skipping as one or more source stub folders are missing")
        package._publish = False
        # TODO Save ?
        return None
    try:
        package.update_package_files()
        package.update_included_stubs()
        package.check()
    except Exception as e:
        log.error(f"{pkg_name}: {e}")
        return None

    # If there are changes to the package, then publish it
    if not (package.is_changed() or force):
        log.info(f"No changes to package : {package.package_name} {package.pkg_version}")
    else:
        if not force:
            log.info(f"Found changes to package : {package.package_name} {package.pkg_version} {package.hash} != {package.create_hash()}")
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
                return None
            result = package.publish(production=production)
            if not result:
                log.warning(f"{pkg_name}: Publish failed for {package.pkg_version}")
                return None
            db.add(package.to_json())
            db.commit()
            # TODO: push to github
            # git add tests\publish\data\package_data_test.jsondb
            # git commit -m "Publish micropython-esp32-stubs (1.18.post24)"
            # git push
            # add tag ?

    if clean:
        package.clean()
    return package.package_name


def publish_multiple(production=False, frozen: bool = False):

    db = get_database(CONFIG.publish_path, production=production)

    worklist = []
    if frozen:
        worklist += list(
            chain(
                frozen_candidates(family="micropython", versions="v1.18", ports="auto", boards="GENERIC"),
            )
        )
    for todo in worklist:
        todo["production"] = False
        todo["dryrun"] = True  # don't publish , dont save to the database
        todo["force"] = False  # publish even if no changes
        todo["clean"] = False  # clean up afterards

        print(todo)
        result = publish(db=db, **todo)
        if result:
            log.info(f"Published {result}")
