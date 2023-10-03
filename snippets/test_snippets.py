import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List

import fasteners
import pytest

log = logging.getLogger()

CORE = ["micropython", "stdlib"]

# features that are not supported by all ports or boards and/or require a specific version
# version notation is >= or <=
PORTBOARD_FEATURES = {
    "stm32": CORE,
    "stm32-pybv11": CORE,
    "esp32": CORE + ["networking", "bluetooth>=1.20.0", "espnow>=1.21.0"],
    "esp8266": CORE + ["networking"],  # TODO: New board stubs for esp8266, "espnow>=1.21.0"],
    "samd": CORE,
    "samd-seeed_wio_terminal": CORE,
    "rp2": CORE,
    "rp2-pico_w>=1.20.0": CORE + ["networking"],  # TODO new board stubs for rp2-pico_w
    "rp2-pimoroni_picolipo_16mb": CORE,
}

SOURCES = ["local", "pypi"]
VERSIONS = ["latest", "v1.20.0", "v1.19.1"]


def pytest_generate_tests(metafunc: pytest.Metafunc):
    """
    Generates a test parameterization for each portboard, version and feature defined in:
    - SOURCES
    - VERSIONS
    - PORTBOARD_FEATURES
    """
    argnames = "stub_source, version, portboard, feature"
    args_lst = []
    for src in SOURCES:
        for version in VERSIONS:
            # skip latest for pypi
            if src == "pypi" and version == "latest":
                continue
            for portboard in PORTBOARD_FEATURES.keys():
                portboard_2, skip_portboard = if_versionfilter(version, portboard)
                if skip_portboard:
                    continue
                port = portboard_2.split("-")[0]
                # add the check_<port> feature
                args_lst.append([src, version, portboard_2, port])
                for feature in PORTBOARD_FEATURES[portboard]:
                    # Check version for features, split feature in name and version
                    feature, skip_feature = if_versionfilter(version, feature)
                    if skip_feature:
                        continue
                    feature = feature.strip()
                    args_lst.append([src, version, portboard_2, feature])
    metafunc.parametrize(argnames, args_lst, scope="session")


def if_versionfilter(version, param):
    skip = False
    if ">=" in param:
        param, min_version = param.split(">=")
        if version != "latest" and version.lstrip("v") < min_version.lstrip("v"):
            skip = True
    if "<=" in param:
        param, max_version = param.split("<=")
        if version != "latest" and version.lstrip("v") > max_version.lstrip("v"):
            skip = True
    return param, skip


def test_pyright(
    stub_source: str,
    version: str,
    portboard: str,
    feature: str,
    snip_path: Path,
    copy_type_stubs: None,  # Avoid needing autouse fixture
    caplog: pytest.LogCaptureFixture,
    pytestconfig: pytest.Config,
):
    if not snip_path or not snip_path.exists():
        FileNotFoundError(f"no feature folder for {feature}")
    caplog.set_level(logging.INFO)

    log.info(f"PYRIGHT {portboard}, {feature} {version} from {stub_source}")

    cmd = f"pyright --project {snip_path.as_posix()} --outputjson"
    typecheck_lock = fasteners.InterProcessLock(snip_path / "typecheck_lock.file")

    results = {}
    with typecheck_lock:
        try:
            # run pyright in the folder with the check_scripts to allow modules to import each other.
            result = subprocess.run(cmd, shell=False, capture_output=True, cwd=snip_path.as_posix())
        except OSError as e:
            raise e
        try:
            results = json.loads(result.stdout)
        except Exception:
            assert 0, "Could not load pyright's JSON output..."

    issues: List[Dict] = results["generalDiagnostics"]
    # log the errors  in the issues list so that pytest will capture the output

    for issue in issues:
        # log file:line:column?: message
        try:
            relative = Path(issue["file"]).relative_to(pytestconfig.rootpath).as_posix()
        except Exception:
            relative = issue["file"]
        msg = f"{relative}:{issue['range']['start']['line']+1}:{issue['range']['start']['character']} {issue['message']}"
        # caplog.messages.append(msg)
        if issue["severity"] == "error":
            log.error(msg)
        elif issue["severity"] == "warning":
            log.warning(msg)
        else:
            log.info(msg)

    info_msg = f"Pyright found {results['summary']['errorCount']} errors and {results['summary']['warningCount']} warnings in {results['summary']['filesAnalyzed']} files."
    assert results["summary"]["errorCount"] == 0, info_msg
    # assert results["summary"]["warningCount"] == 0, info_msg

    # return issues
