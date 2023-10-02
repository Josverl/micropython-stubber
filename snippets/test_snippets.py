import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List

import pytest

log = logging.getLogger()

ALL = ["common", "stdlib", "micropython"]

# features that are not supported by all ports or boards and/or require a specific version
# version notation is >= or <=
PORTBOARD_FEATURES = {
    "stm32": ALL,
    "esp32": ALL + ["networking", "bluetooth>=1.20.0", "espnow>=1.21.0"],
    "esp8266": ALL + ["networking"],  # TODO: New board stubs for esp8266, "espnow>=1.21.0"],
    "samd": ALL,
    "rp2": ALL,
    "rp2-pico_w": ALL + ["networking"],
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
                port = portboard.split("-")[0]
                args_lst.append([src, version, portboard, port])
                for feature in PORTBOARD_FEATURES[portboard]:
                    # Check version for features, split feature in name and version
                    if ">=" in feature:
                        feature, min_version = feature.split(">=")
                        if version != "latest" and version.lstrip("v") < min_version.lstrip("v"):
                            continue
                    if "<=" in feature:
                        feature, max_version = feature.split("<=")
                        if version != "latest" and version.lstrip("v") > max_version.lstrip("v"):
                            continue
                    feature = feature.strip()
                    args_lst.append([src, version, portboard, feature])
    metafunc.parametrize(argnames, args_lst, scope="session")


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
    caplog.set_level(logging.INFO)

    log.info(f"PYRIGHT {portboard}, {feature} {version} from {stub_source}")
    if not snip_path or not snip_path.exists():
        FileNotFoundError(f"no feature folder for {feature}")

    cmd = f"pyright --project {snip_path.as_posix()} --outputjson"

    results = {}
    try:
        # run pyright in the docstub folder to allow modules to import each other.
        result = subprocess.run(cmd, shell=False, capture_output=True, cwd=snip_path.as_posix())
    except OSError as e:
        raise e
    try:
        results = json.loads(result.stdout)
    except Exception:
        assert 0, "Could not load pyright's JSON output..."

    issues: List[Dict] = results["generalDiagnostics"]
    # log the errors  in the issues list so that pytest will capture the output
    print("ISSUES", issues)
    for issue in issues:
        # log file:line:column?: message
        relative = Path(issue["file"]).relative_to(pytestconfig.rootpath).as_posix()
        msg = f"{relative}:{issue['range']['start']['line']+1}:{issue['range']['start']['character']} {issue['message']}"
        # caplog.messages.append(msg)
        if issue["severity"] == "error":
            log.error(msg)
        elif issue["severity"] == "warning":
            log.warning(msg)

    info_msg = f"Pyright found {results['summary']['errorCount']} errors and {results['summary']['warningCount']} warnings in {results['summary']['filesAnalyzed']} files."
    assert results["summary"]["errorCount"] == 0, info_msg
    # assert results["summary"]["warningCount"] == 0, info_msg

    # return issues
