import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List

import fasteners
import pytest
from packaging.version import Version

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
    "samd-ADAFRUIT_ITSYBITSY_M4_EXPRESS": CORE,
    "rp2": CORE,
    "rp2-RPI_PICO": CORE,
    # TODO new board stubs for rp2-pico_w
    # TODO new board stubs for rp2-rpi_pico_w
    "rp2-pico_w>=1.20.0": CORE + ["networking"],
    "rp2-rpi_pico_w>=1.20.0": CORE + ["networking", "bluetooth>=1.20.0"],
    "rp2-pimoroni_picolipo_16mb": CORE,
}

SOURCES = ["local", "pypi"]
VERSIONS = ["latest", "v1.21.0", "v1.20.0"]  # , "v1.19.1"]


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
                portboard_2, skip_portboard = skip_versionfilter(version, portboard)
                if skip_portboard:
                    continue
                port = portboard_2.split("-")[0]
                # add the check_<port> feature
                args_lst.append([src, version, portboard_2, port])
                for feature in PORTBOARD_FEATURES[portboard]:
                    # Check version for features, split feature in name and version
                    feature, skip_feature = skip_versionfilter(version, feature)
                    if skip_feature:
                        continue
                    feature = feature.strip()
                    args_lst.append([src, version, portboard_2, feature])
    metafunc.parametrize(argnames, args_lst, scope="session")


def skip_versionfilter(version, param):
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


def filter_issues(issues: List[Dict], version: str, portboard: str = ""):
    port, board = portboard.split("-") if "-" in portboard else (portboard, "")
    for issue in issues:
        filename = Path(issue["file"])
        with open(filename, "r") as f:
            lines = f.readlines()
        line = issue["range"]["start"]["line"]
        if len(lines) > line:
            theline: str = lines[line]
            # check if the line contains a stubs-ignore comment
            if stub_ignore(theline, version, port, board):
                issue["severity"] = "information"
    return issues


def stub_ignore(line, version, port, board, linter="pyright"):
    """
    Check if a tyoecheck error should be ignored based on the version of micropython , the port and the board

    format of the source  :

        import espnow # stubs-ignore: version<1.21.0 or not port.startswith('esp')

    """
    comment = line.rsplit("#")[-1].strip()
    if not (comment.startswith("stubs-ignore") and ":" in comment):
        return False
    id, condition = comment.split(":")
    if id.strip() != "stubs-ignore":
        return False
    context = {}
    context["Version"] = Version
    context["version"] = Version(version) if version != "latest" else Version("9999.99.99")
    context["port"] = port
    context["board"] = board
    context["linter"] = linter

    try:
        # transform : version>=1.20.1 to version>=Version('1.20.1') using a regular expression
        condition = re.sub(r"(\d+\.\d+\.\d+)", r"Version('\1')", condition.strip())
        print(condition)
        result = eval(condition, context)
    except Exception as e:
        log.warning(f"Incorrect stubs-ignore condition: `{condition}`\ncaused: {e}")
        result = None

    return result


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
            result = subprocess.run(
                cmd, shell=False, capture_output=True, cwd=snip_path.as_posix()
            )
        except OSError as e:
            raise e
        if result.returncode >= 2:
            assert (
                0
            ), f"Pyright failed with returncode {result.returncode}: {result.stdout}\n{result.stderr}"
        try:
            results = json.loads(result.stdout)
        except Exception:
            assert 0, "Could not load pyright's JSON output..."

    issues: List[Dict] = results["generalDiagnostics"]
    # for each of the issues - retrieve the line in the source file to inspect if has a trailing comment
    issues = filter_issues(issues, version, portboard)

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
    errorcount = len([i for i in issues if i["severity"] == "error"])
    assert errorcount == 0, info_msg

    # return issues
