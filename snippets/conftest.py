"""Pytest configuration file for snippets tests.

- snip_path
  returns the path to the feature folder (feat_xxxx) or check folder (check_xxxx)

- type_stub_cache_path
  Is used to install the type stubs for the given portboard and version and cache it for 24 hours to speed up tests
  Returns the path to the cache folder

- install_stubs
  is the function that does the actual pip install to a folder

- copy_type_stubs
  copies the type stubs from the cache to the feature folder

- pytest_runtest_makereport 
  is used to add the caplog to the test report to make it avaialble to VSCode test explorer

"""

import json
import shutil
import subprocess
import time
from pathlib import Path

import fasteners
import pytest
from loguru import logger as log

SNIPPETS_PREFIX = "snippets/"
MAX_CACHE_AGE = 24 * 60 * 60


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    pytest_runtest_makereport hook implementation.

    Executes all other hooks to obtain the report object. Looks at actual failing test calls, not setup/teardown. Adds the caplog errors and warnings to the report.

    Args:
        item: The pytest Item object.
        call: The pytest CallInfo object.

    Returns:
        The pytest Report object.

    """
    outcome = yield
    report = outcome.get_result()

    # we only look at actual failing test calls, not setup/teardown
    if report.when == "call" and report.failed:
        # add the caplog errors and warnings to the report
        if not "caplog" in item.funcargs:
            return
        caplog = item.funcargs["caplog"]
        report_txt = (
            "\n"
            + "\n".join([r.message for r in caplog.records])
            + "\n\n"
            + str(report.longreprtext)
        )
        report.longrepr = report_txt

        return report


@pytest.fixture(scope="session")
def type_stub_cache_path(
    portboard: str,
    version: str,
    stub_source: str,
    pytestconfig: pytest.Config,
    request: pytest.FixtureRequest,
) -> Path:
    """
    Installs a copy of the type stubs for the given portboard and version. Returns the path to the cache folder.

    Args:
        portboard: The portboard.
        version: The version.
        stub_source: The stub source.
        pytestconfig: The pytest Config object.
        request: The pytest FixtureRequest object.

    Returns:
        Path: The path to the cache folder.
    """

    log.trace(f"setup install type_stubs to cache: {stub_source}, {version}, {portboard}")
    flatversion = version.replace(".", "_")
    cache_key = f"stubber/{stub_source}/{version}/{portboard}"
    # cache_path = pytestconfig.rootpath / "snippets" / "typings_cache"
    tsc_path = Path(
        request.config.cache.makedir(f"typings_{flatversion}_{portboard}_stub_{stub_source}")
    )
    # prevent simultaneous updates to the cache
    cache_lock = fasteners.InterProcessLock(tsc_path.parent / f"{tsc_path.name}.lock")
    # check if stubs are already installed to the cache
    with cache_lock:
        if (tsc_path / "micropython.pyi").exists():
            # check if stubs are in the cache
            timestamp = request.config.cache.get(cache_key, None)
            # if timestamp is not older than 24 hours, use cache

            if timestamp and timestamp > (time.time() - MAX_CACHE_AGE):
                log.trace(f"Using cached type stubs for {portboard} {version}")
                return tsc_path

        ok = install_stubs(portboard, version, stub_source, pytestconfig, flatversion, tsc_path)
        if not ok:
            pytest.skip(f"Could not install stubs for {portboard} {version}")
        # add the timestamp to the cache
        request.config.cache.set(cache_key, time.time())

    return tsc_path


def install_stubs(
    portboard, version, stub_source, pytestconfig, flatversion, tsc_path: Path
) -> bool:
    """
    Cleans up prior install to avoid stale files.
    Uses pip to install type stubs for the given portboard and version.

    Args:
        portboard: The portboard.
        version: The version.
        stub_source: The stub source.
        pytestconfig: The pytest Config object.
        flatversion: The flat version.
        tsc_path: The path to the cache folder.

    Returns:
        bool: True if the installation was successful, False otherwise.
    """

    # clean up prior install to avoid stale files
    if tsc_path.exists():
        shutil.rmtree(tsc_path, ignore_errors=True)
    # use pip to install type stubs
    # Install type stubs for portboard and version
    if stub_source == "pypi":
        # Add version
        cmd = f"pip install micropython-{portboard}-stubs=={version.lower().lstrip('v')}.* --target {tsc_path} --no-user"
    else:
        foldername = f"micropython-{flatversion}-{portboard}-stubs"
        stubsource = pytestconfig.inipath.parent / f"repos/micropython-stubs/publish/{foldername}"
        if not stubsource.exists():
            pytest.skip(f"Could not find stubs for {portboard} {version} at {stubsource}")
        cmd = f"pip install {stubsource} --target {tsc_path} --no-user"

    try:
        subprocess.run(cmd, shell=False, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        # skip test if source connot be found
        print(f"{e.stderr}")
        pytest.skip(f"{e.stderr}")
        return False
    return True


@pytest.fixture(scope="function")
def snip_path(feature: str, pytestconfig) -> Path:
    """
    Get the path to the feat_ or check_ folder.

    Args:
        feature: The feature.
        pytestconfig: The pytest Config object.

    Returns:
        Path: The path to the feature folder.
    """

    snip_path = pytestconfig.inipath.parent / "snippets" / f"feat_{feature}"
    if not snip_path.exists():
        snip_path = pytestconfig.inipath.parent / "snippets" / f"check_{feature}"
    return snip_path


@pytest.fixture(scope="function")
def copy_type_stubs(
    portboard: str, version: str, feature: str, type_stub_cache_path: Path, snip_path: Path
):
    """
    Copies installed/cached type stubs from the cache to the feature folder.

    Args:
        portboard: The portboard.
        version: The version.
        feature: The feature.
        type_stub_cache_path: The path to the cache folder.
        snip_path: The path to the feature folder.
    """
    cache_lock = fasteners.InterProcessLock(
        type_stub_cache_path.parent / f"{type_stub_cache_path.name}.lock"
    )
    typecheck_lock = fasteners.InterProcessLock(snip_path / "typecheck_lock.file")
    with cache_lock:
        with typecheck_lock:
            log.trace(f"- copy_type_stubs: {version}, {portboard} to {feature}")
            print(f"\n - copy_type_stubs : {version}, {portboard} to {feature}")
            if not snip_path or not snip_path.exists():
                # skip if no feature folder
                pytest.skip(f"no feature folder for {feature}")
            typings_path = snip_path / "typings"
            if typings_path.exists():
                shutil.rmtree(typings_path, ignore_errors=True)
            shutil.copytree(type_stub_cache_path, typings_path)


def pytest_terminal_summary(terminalreporter, exitstatus, config: pytest.Config):
    stats = {}
    for status in ["passed", "failed", "xfailed", "skipped"]:
        stats[status] = snipcount(terminalreporter, status)
    # simple straigth forward scoring
    stats["snippet_score"] = int(stats["passed"] - stats["failed"])
    if stats["snippet_score"] >= 0:
        # Write stats to file
        (config.rootpath / "coverage").mkdir(exist_ok=True)
        with open(config.rootpath / "coverage" / "snippet_score.json", "w") as f:
            json.dump(stats, f, indent=4)

        print("----------------- terminal summary -----------------")
        print(json.dumps(stats, indent=4))
        print("----------------------------------------------------")


def snipcount(terminalreporter, status: str):
    # Count the number of test snippets that have a given status
    if not terminalreporter.stats.get(status, []):
        return 0
    return len(
        [rep for rep in terminalreporter.stats[status] if rep.nodeid.startswith(SNIPPETS_PREFIX)]
    )
