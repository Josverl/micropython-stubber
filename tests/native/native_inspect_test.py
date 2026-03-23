# Test createstubs.py with the inspect module on real MicroPython unix port.
#
# Uses the pre-built MicroPython binaries stored in tests/tools/ — never the
# system-installed micropython, which may be very old or absent.
# The MicroPython inspect module (tests/data/mpy_inspect.py) is copied into the
# working directory so that createstubs can import it, exactly as a user would
# deploy it on a device alongside createstubs.py.
#
# Tests verify that:
#   1. createstubs.py runs without errors with inspect available.
#   2. Functions get actual parameter counts (x0, x1, …) instead of *args/**kwargs.
#   3. Class method stubs have 'self' exactly once (no duplication).
#   4. Coroutine / async-generator functions are emitted as 'async def'.

import json
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = [pytest.mark.stubber, pytest.mark.native]

# ---------------------------------------------------------------------------
# Locate a usable MicroPython binary from tests/tools/ only.
# ---------------------------------------------------------------------------

_TOOLS = Path(__file__).parent.parent / "tools"
_MPY_INSPECT = Path(__file__).parent.parent / "data" / "mpy_inspect.py"


def _find_micropython_in_tools() -> str:
    """Return the path of the first executable MicroPython binary in tests/tools/,
    or an empty string if none is found.  Never falls back to the system path."""
    # Prefer newer Ubuntu builds; fall back to older ones in order.
    # Each glob pattern is relative to _TOOLS.  Add new entries here when new
    # pre-built binaries are checked in.
    search_patterns = [
        "ubuntu_24_04/micropython_v*",
        "ubuntu_20_04/micropython_v1_2*",
    ]
    candidates: list[Path] = []
    for pattern in search_patterns:
        candidates.extend(sorted(_TOOLS.glob(pattern)))

    for binary in candidates:
        try:
            r = subprocess.run(
                [str(binary), "-c", "import sys; print(sys.version)"],
                capture_output=True,
                timeout=5,
            )
            if r.returncode == 0 and b"MicroPython" in r.stdout:
                return str(binary)
        except Exception:
            pass
    return ""


_MICROPYTHON = _find_micropython_in_tools()

_skip_no_mpy = pytest.mark.skipif(
    not _MICROPYTHON,
    reason="No usable MicroPython binary found in tests/tools/",
)
_skip_no_inspect = pytest.mark.skipif(
    not _MPY_INSPECT.exists(),
    reason="tests/data/mpy_inspect.py fixture not found",
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _run_createstubs(micropython: str, script_path: Path, work_dir: Path, with_inspect: bool = True) -> Path:
    """Copy createstubs.py (and optionally inspect.py) into *work_dir*, run it,
    and return the stubs output directory."""
    stub_out = work_dir / "stubs"
    stub_out.mkdir(exist_ok=True)

    shutil.copy(script_path / "createstubs.py", work_dir / "createstubs.py")
    if with_inspect:
        shutil.copy(_MPY_INSPECT, work_dir / "inspect.py")

    result = subprocess.run(
        [micropython, "createstubs.py", "--path", str(stub_out)],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        pytest.fail(
            f"createstubs.py exited {result.returncode}:\n{result.stderr}\n{result.stdout}"
        )
    return stub_out


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@_skip_no_mpy
@_skip_no_inspect
def test_createstubs_with_inspect_runs(tmp_path: Path, pytestconfig):
    """createstubs.py must complete without errors when inspect.py is available."""
    script_path = (pytestconfig.rootpath / "src" / "stubber" / "board").absolute()
    stub_out = _run_createstubs(_MICROPYTHON, script_path, tmp_path)

    stubs = list(stub_out.rglob("*.pyi"))
    assert stubs, "at least one stub should be generated"

    manifests = list(stub_out.rglob("modules.json"))
    assert len(manifests) == 1, "exactly one modules.json must be created"

    manifest = json.loads(manifests[0].read_text())
    for key in ("firmware", "stubber", "modules"):
        assert key in manifest, f"manifest missing key: {key}"
    assert len(manifest["modules"]) == len(stubs), "stub count must match manifest"


@_skip_no_mpy
@_skip_no_inspect
def test_inspect_improves_param_signatures(tmp_path: Path, pytestconfig):
    """With inspect, functions should have concrete parameter names (x0, x1 …)
    rather than the generic *args/**kwargs fallback.

    MicroPython's inspect.signature() returns dummy names x0, x1, … but the
    count is correct.  At least some single-argument functions in 'uos'/'os'
    should appear as ``def f(x0) -> Incomplete`` instead of
    ``def f(*args, **kwargs) -> Incomplete``.
    """
    script_path = (pytestconfig.rootpath / "src" / "stubber" / "board").absolute()
    stub_out = _run_createstubs(_MICROPYTHON, script_path, tmp_path)

    uos_stub = next(stub_out.rglob("uos.pyi"), None) or next(stub_out.rglob("os.pyi"), None)
    assert uos_stub is not None, "uos.pyi / os.pyi should exist"

    content = uos_stub.read_text(encoding="utf-8")
    # At least one function should have a concrete positional param (x0)
    assert "(x0)" in content or "(x0," in content, (
        "uos stub should have functions with concrete param names when inspect is available"
    )


@_skip_no_mpy
@_skip_no_inspect
def test_class_method_no_double_self(tmp_path: Path, pytestconfig):
    """Class method stubs must not have 'self' listed twice.

    On MicroPython, inspect.signature() uses dummy names (x0, x1, …) where
    x0 represents 'self'.  The stub generator must strip that first parameter
    and prepend exactly one explicit 'self', never producing 'self, x0, …'.
    """
    script_path = (pytestconfig.rootpath / "src" / "stubber" / "board").absolute()
    stub_out = _run_createstubs(_MICROPYTHON, script_path, tmp_path)

    doubled = [
        p.name
        for p in stub_out.rglob("*.pyi")
        if "self, self" in p.read_text(encoding="utf-8")
        or "(self, x0" in p.read_text(encoding="utf-8")
    ]
    assert not doubled, (
        "self is duplicated in class-method stubs: " + ", ".join(doubled)
    )


@_skip_no_mpy
@_skip_no_inspect
def test_async_functions_emit_async_def(tmp_path: Path, pytestconfig):
    """Coroutine functions (type 'generator' on MicroPython) should produce
    'async def' stubs when inspect is available.

    asyncio contains well-known coroutines (gather, wait_for, open_connection,
    start_server).  On MicroPython they have type 'generator'; inspect detects
    them via iscoroutinefunction() and the stub generator should emit 'async def'.
    """
    script_path = (pytestconfig.rootpath / "src" / "stubber" / "board").absolute()
    stub_out = _run_createstubs(_MICROPYTHON, script_path, tmp_path)

    asyncio_stub = next(stub_out.rglob("asyncio/__init__.pyi"), None) or next(
        stub_out.rglob("uasyncio/__init__.pyi"), None
    )
    if asyncio_stub is None:
        pytest.skip("asyncio/__init__.pyi not generated on this MicroPython build")

    content = asyncio_stub.read_text(encoding="utf-8")
    assert "async def" in content, (
        "asyncio stub should contain 'async def' for coroutine functions.\n"
        f"Got (first 600 chars):\n{content[:600]}"
    )
