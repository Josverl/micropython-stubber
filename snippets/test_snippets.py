import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List

import fasteners
import pytest
from packaging.version import Version

# only snippets tests
pytestmark = pytest.mark.snippets

log = logging.getLogger()

CORE = ["micropython", "stdlib", "uasyncio:skip port=='esp8266'"]

# features that are not supported by all ports or boards and/or require a specific version
# format: <port>-<board>:<condition> or <feature>:<condition>
# if the conditon IS met, the feature is skipped - so please read as SKIP if condition or prefix with 'skip'
# condition: version<1.21.0 or not port.startswith('esp')
PORTBOARD_FEATURES = {
    "stm32": CORE,
    "stm32-pybv11": CORE,
    "esp32": CORE
    + [
        "networking",
        "bluetooth:skip version<1.20.0",
        "espnow:skip version<1.21.0",
    ],
    "esp8266": CORE + ["networking"],  # TODO: New board stubs for esp8266, "espnow>=1.21.0"],
    "samd": CORE,
    "samd-seeed_wio_terminal": CORE,
    # "samd-ADAFRUIT_ITSYBITSY_M4_EXPRESS": CORE,
    "rp2": CORE,
    "rp2-pico:skip version>1.20.0": CORE,  # renamed later to rp2-rpi_pico
    "rp2-pico_w:skip version>1.20.0": CORE + ["networking"],
    #
    "rp2-rpi_pico:skip version<1.21.0": CORE,
    "rp2-rpi_pico_w:skip version<1.21.0": CORE
    + [
        "networking",
        "bluetooth:skip version<1.21.0",
    ],
    # "rp2-pimoroni_picolipo_16mb": CORE,
}

SOURCES = ["local", "pypi"]
VERSIONS = [
    "latest",
    "v1.21.0",
    "v1.20.0",
    "v1.19.1",
    # "v1.18",
]


def port_and_board(portboard):
    if "-" in portboard:
        port, board = portboard.split("-", 1)
    else:
        port, board = portboard, ""
    return port, board


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
            for key in PORTBOARD_FEATURES.keys():
                portboard = key
                if ":" in portboard:
                    portboard, condition = portboard.split(":", 1)
                    port, board = port_and_board(portboard)
                    if stub_ignore(
                        condition, version, port, board, linter="pytest", is_source=False
                    ):
                        continue
                else:
                    port, board = port_and_board(portboard)

                # add the check_<port> feature
                args_lst.append([src, version, portboard, port])
                for feature in PORTBOARD_FEATURES[key]:
                    if ":" in feature:
                        # Check version for features, split feature in name and version
                        feature, condition = feature.split(":", 1)
                        if stub_ignore(
                            condition, version, port, board, linter="pytest", is_source=False
                        ):
                            continue
                    feature = feature.strip()
                    args_lst.append([src, version, portboard, feature])
    metafunc.parametrize(argnames, args_lst, scope="session")


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


def stub_ignore(line, version, port, board, linter="pyright", is_source=True) -> bool:
    """
    Check if a typecheck error should be ignored based on the version of micropython , the port and the board
    the same syntax can be used in the source file or in the test case condition :

    format of the source line (is_source=True)
        import espnow # stubs-ignore: version<1.21.0 or not port.startswith('esp')

    or condition (is_source=False) line:
        version<1.21.0
        skip version<1.21.0 # skip prefix to helps human understanding / reading
        skip port.startswith('esp')
    """
    if is_source:
        comment = line.rsplit("#")[-1].strip()
        if not (comment.startswith("stubs-ignore") and ":" in comment):
            return False
        id, condition = comment.split(":")
        if id.strip() != "stubs-ignore":
            return False
    else:
        condition = line.strip()
    if condition.lower().startswith("skip"):
        condition = condition[4:].strip()
    context = {}
    context["Version"] = Version
    context["version"] = Version(version) if version != "latest" else Version("9999.99.99")
    context["port"] = port
    context["board"] = board
    context["linter"] = linter

    try:
        # transform : version>=1.20.1 to version>=Version('1.20.1') using a regular expression
        condition = re.sub(r"(\d+\.\d+\.\d+)", r"Version('\1')", condition.strip())
        result = eval(condition, context)
        print(f'stubs-ignore: {condition} -> {"Skip" if result else "Process"}')
    except Exception as e:
        log.warning(f"Incorrect stubs-ignore condition: `{condition}`\ncaused: {e}")
        result = False

    return bool(result)


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
            result = subprocess.run(cmd, shell=True, capture_output=True, cwd=snip_path.as_posix())
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
