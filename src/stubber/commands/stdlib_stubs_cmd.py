"""
Command line interface to build micropython-stdlib-stubs package.

This command integrates the functionality of building stdlib stubs from typeshed
and merging them with MicroPython documentation stubs.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

import rich_click as click
from mpflash.logger import log
from mpflash.versions import clean_version, get_stable_mp_version

from stubber.codemod.enrich import enrich_folder
from stubber.commands.cli import stubber_cli
from stubber.modcat import STDLIB_ONLY_MODULES
from stubber.utils import do_post_processing
from stubber.utils.config import CONFIG

# These modules will be kept in the stdlib folder
STDLIB_MODULES_TO_KEEP = list(
    set(STDLIB_ONLY_MODULES)
    | set(
        [
            "_typeshed",
            "asyncio",
            "collections",
            "sys",
            "os",
            "__future__",
            "_ast",
            "_codecs",
            "_collections_abc",
            "_decimal",
            "abc",
            "array",
            "builtins",
            "io",
            "re",
            "sys",
            "types",
            "typing_extensions",
            "typing",
            "tls",
            "ssl",
            "enum",
            "sre_compile",
            "sre_constants",
            "sre_parse",
        ]
    )
)

# Try to limit the "overspeak" of python modules to the bare minimum
STDLIB_MODULES_TO_REMOVE = [
    "os/path.pyi",
    "sys/_monitoring.pyi",
    "asyncio/subprocess.pyi",
    "asyncio/base_subprocess.pyi",
    "asyncio/taskgroups.pyi",
    "asyncio/windows_events.pyi",
    "asyncio/windows_utils.pyi",
    "json/decoder.pyi",
    "json/encoder.pyi",
    "json/tool.pyi",
]

# Type ignore patterns
TYPE_IGNORES = [
    ("os", ["path = _path"]),
    ("asyncio/taskgroups", [": Context", "from contextvars import Context"]),
    ("asyncio/base_events", [": Context", "from contextvars import Context"]),
    ("asyncio/base_futures", [": Context", "from contextvars import Context"]),
    ("asyncio/events", [": Context", "from contextvars import Context"]),
    ("asyncio/runners", [": Context", "from contextvars import Context"]),
    ("_typeshed", ["Field[Any]"]),
    (
        "builtins",
        [
            ": int = -1",
            ": int = 0",
            " | None = None",
            ": bool = True",
            ": bool = False",
            ': str | None = "',
            ': str = "',
            '| bytearray = b"',
            ': bytes = b"',
        ],
    ),
    (
        "collections",
        [
            "deque[_T]",
            "OrderedDict[",
            "class deque(stdlib_deque):",
            "class OrderedDict(stdlib_OrderedDict):",
            ": _T, /",
            "[_KT, _VT]",
            ": _T,",
            ": _KT,",
            ": _VT,",
            "-> _T:",
            "-> _KT:",
            "-> _VT:",
            "Iterator[_T]",
            "Iterator[_KT]",
        ],
    ),
    ("io", ["from io import *"]),
]

# Comment out some lines to hide CPython APIs
COMMENT_OUT_LINES = [
    ("asyncio", ["from .subprocess import *"]),
    (
        "os",
        [
            "from . import path as _path",
            "def _exit(status: int) -> NoReturn: ...",
        ],
    ),
]

# Change some lines to hide CPython APIs
CHANGE_LINES = [
    (
        "ssl",
        [
            ("def create_default_context", "def __mpy_has_no_create_default_context"),
            ("if sys.version_info < (3, 12):", "if True:"),
        ],
    ),
    (
        "sys",
        [
            ("def _getframe(", "def __mpy_has_no_getframe("),
        ],
    ),
]


def _extract_error_lines(text: str, max_lines: int = 10) -> str:
    """Extract concise error lines from command output."""
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    if len(lines) > max_lines:
        lines = lines[-max_lines:]
    return "\n".join(lines)


def update_stdlib_from_typeshed(dist_stdlib_path: Path, typeshed_path: Path) -> None:
    """Update stdlib folder from typeshed repository."""
    log.info("Updating stdlib from typeshed")

    # Clear the stdlib folder
    stdlib_path = dist_stdlib_path / "stdlib"
    if stdlib_path.exists():
        shutil.rmtree(stdlib_path)
    stdlib_path.mkdir(parents=True, exist_ok=True)

    # Copy modules from typeshed
    typeshed_stdlib = typeshed_path / "stdlib"
    if not typeshed_stdlib.exists():
        raise FileNotFoundError(f"Typeshed stdlib path not found: {typeshed_stdlib}")

    for module in STDLIB_MODULES_TO_KEEP:
        src_path = typeshed_stdlib / module
        if src_path.is_file():
            # Single file module
            dst_path = stdlib_path / module
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            log.debug(f"Copied {module}")
        elif src_path.is_dir():
            # Package module
            dst_path = stdlib_path / module
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            log.debug(f"Copied package {module}")
        else:
            # Try with .pyi extension
            src_pyi = typeshed_stdlib / f"{module}.pyi"
            if src_pyi.exists():
                dst_path = stdlib_path / f"{module}.pyi"
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_pyi, dst_path)
                log.debug(f"Copied {module}.pyi")

    # Remove unwanted modules
    for module_path in STDLIB_MODULES_TO_REMOVE:
        full_path = stdlib_path / module_path
        if full_path.exists():
            full_path.unlink()
            log.debug(f"Removed {module_path}")


def update_mpy_shed(reference_path: Path, dist_stdlib_path: Path) -> None:
    """Update _mpy_shed stubs from reference folder."""
    log.info("Updating _mpy_shed")
    src_mpy_shed = reference_path / "_mpy_shed"
    dst_mpy_shed = dist_stdlib_path / "stdlib" / "_mpy_shed"

    if src_mpy_shed.exists():
        if dst_mpy_shed.exists():
            shutil.rmtree(dst_mpy_shed)
        shutil.copytree(src_mpy_shed, dst_mpy_shed, dirs_exist_ok=True)
        log.debug("Updated _mpy_shed")


def update_asyncio_manual(reference_path: Path, dist_stdlib_path: Path) -> None:
    """Update manually maintained asyncio stubs."""
    log.info("Updating asyncio manual stubs")
    src_asyncio = reference_path / "asyncio"
    dst_asyncio = dist_stdlib_path / "stdlib" / "asyncio"

    if src_asyncio.exists():
        shutil.copytree(src_asyncio, dst_asyncio, dirs_exist_ok=True)
        log.debug("Updated asyncio stubs")


def merge_docstubs_into_stdlib(
    dist_stdlib_path: Path,
    docstubs_path: Path,
    boardstub_path: Path,
) -> None:
    """Merge documentation stubs into stdlib."""
    log.info("Merging docstubs into stdlib")
    stdlib_path = dist_stdlib_path / "stdlib"

    # Merge from docstubs
    if docstubs_path.exists():
        result = enrich_folder(
            stub_folder=stdlib_path,
            docstub_folder=docstubs_path,
        )
        log.info(f"Merged {result} files from docstubs")

    # Merge from board stubs
    if boardstub_path.exists():
        result = enrich_folder(
            stub_folder=stdlib_path,
            docstub_folder=boardstub_path,
        )
        log.info(f"Merged {result} files from board stubs")


def add_type_ignore(stdlib_path: Path) -> None:
    """Add type ignore comments to reduce typechecker noise."""
    log.info("Adding type ignore comments")

    for module, patterns in TYPE_IGNORES:
        module_file = stdlib_path / f"{module}.pyi"
        if not module_file.exists():
            continue

        content = module_file.read_text(encoding="utf-8")
        modified = False

        for pattern in patterns:
            if pattern in content:
                # Add # type: ignore comment at end of lines containing pattern
                lines = content.split("\n")
                new_lines = []
                for line in lines:
                    if pattern in line and "# type: ignore" not in line:
                        line = line.rstrip() + "  # type: ignore"
                        modified = True
                    new_lines.append(line)
                content = "\n".join(new_lines)

        if modified:
            module_file.write_text(content, encoding="utf-8")
            log.debug(f"Added type ignores to {module}")


def comment_out_lines(stdlib_path: Path) -> None:
    """Comment out lines that cause issues."""
    log.info("Commenting out problematic lines")

    for module, patterns in COMMENT_OUT_LINES:
        module_file = stdlib_path / f"{module}.pyi"
        if not module_file.exists():
            continue

        content = module_file.read_text(encoding="utf-8")
        modified = False

        for pattern in patterns:
            if pattern in content:
                content = content.replace(pattern, f"# {pattern}")
                modified = True

        if modified:
            module_file.write_text(content, encoding="utf-8")
            log.debug(f"Commented out lines in {module}")


def change_lines(stdlib_path: Path) -> None:
    """Change lines to hide CPython APIs."""
    log.info("Changing problematic lines")

    for module, replacements in CHANGE_LINES:
        module_file = stdlib_path / f"{module}.pyi"
        if not module_file.exists():
            continue

        content = module_file.read_text(encoding="utf-8")
        modified = False

        for old_text, new_text in replacements:
            if old_text in content:
                content = content.replace(old_text, new_text)
                modified = True

        if modified:
            module_file.write_text(content, encoding="utf-8")
            log.debug(f"Changed lines in {module}")


def update_typing_pyi(rootpath: Path, dist_stdlib_path: Path) -> None:
    """Update typing.pyi with patches."""
    log.info("Updating typing.pyi")
    # Placeholder for typing.pyi specific patches if needed


@stubber_cli.command(name="stdlib")
@click.option(
    "--version",
    "-v",
    type=str,
    help="Specify MicroPython version",
    default=None,
    show_default=True,
)
@click.option(
    "--update/--no-update",
    "-u",
    help="Update stdlib from the typeshed repo.",
    default=False,
    show_default=True,
)
@click.option(
    "--merge/--no-merge",
    "-m",
    help="Merge the docstubs into the stdlib.",
    default=True,
    show_default=True,
)
@click.option(
    "--publish/--no-publish",
    help="Publish the stdlib-stubs module.",
    default=False,
    show_default=True,
)
@click.option(
    "--build/--no-build",
    "-b",
    help="Build the stdlib-stubs module.",
    default=True,
    show_default=True,
)
def cli_stdlib_stubs(
    version: Optional[str] = None,
    update: bool = False,
    merge: bool = True,
    build: bool = True,
    publish: bool = False,
):
    """
    Build the micropython-stdlib-stubs package.

    This command manages the creation of the stdlib-stubs package by:
    - Updating from typeshed repository
    - Merging with MicroPython documentation stubs
    - Post-processing and formatting
    - Building and optionally publishing the package
    """
    # Determine version
    if not version:
        version = get_stable_mp_version()

    flat_version = clean_version(version, flat=True, drop_v=False)
    log.info(f"Build micropython-stdlib-stubs for version: {version}")

    # Determine paths based on CONFIG
    rootpath = CONFIG.stub_path.parent if CONFIG.stub_path else Path.cwd()
    log.info(f"Using rootpath: {rootpath}")

    dist_stdlib_path = rootpath / "publish/micropython-stdlib-stubs"
    docstubs_path = rootpath / f"stubs/micropython-{flat_version}-docstubs"
    boardstub_path = rootpath / f"stubs/micropython-{flat_version}-esp32-ESP32_GENERIC"
    typeshed_path = CONFIG.repo_path / CONFIG.typeshed_path
    reference_path = rootpath / "reference"

    # Validate required paths
    if not rootpath.exists():
        raise click.ClickException(f"Root path {rootpath} does not exist")

    # Create dist_stdlib_path if it doesn't exist
    dist_stdlib_path.mkdir(parents=True, exist_ok=True)

    if update:
        if not typeshed_path.exists():
            raise click.ClickException(
                f"Typeshed path {typeshed_path} does not exist. Please clone it first using: stubber clone --typeshed"
            )
        update_stdlib_from_typeshed(dist_stdlib_path, typeshed_path)

    # Always update _mpy_shed and asyncio
    if reference_path.exists():
        update_mpy_shed(reference_path, dist_stdlib_path)
        update_asyncio_manual(reference_path, dist_stdlib_path)

    if merge:
        if not docstubs_path.exists():
            log.warning(f"Docstubs path {docstubs_path} does not exist, skipping merge")
        else:
            merge_docstubs_into_stdlib(
                dist_stdlib_path=dist_stdlib_path,
                docstubs_path=docstubs_path,
                boardstub_path=boardstub_path if boardstub_path.exists() else None,
            )

    # Post-process the stubs
    stdlib_path = dist_stdlib_path / "stdlib"
    if stdlib_path.exists():
        do_post_processing([stdlib_path], stubgen=False, format=True, autoflake=True)
        add_type_ignore(stdlib_path)
        comment_out_lines(stdlib_path)
        change_lines(stdlib_path)

    # Update last changed time
    pyproject_path = dist_stdlib_path / "pyproject.toml"
    if pyproject_path.exists():
        pyproject_path.touch()

    # Update typing.pyi
    update_typing_pyi(rootpath, dist_stdlib_path)

    if build or publish:
        if not (dist_stdlib_path / "pyproject.toml").exists():
            raise click.ClickException(f"No pyproject.toml found in {dist_stdlib_path}. Cannot build package.")

        try:
            log.info("Building stdlib-stubs package...")
            subprocess.check_call(
                ["uv", "build", "--index-strategy", "unsafe-best-match"],
                cwd=dist_stdlib_path,
            )
            log.info("Build completed successfully")
        except subprocess.CalledProcessError as e:
            msg = _extract_error_lines(getattr(e, "stderr", "") or getattr(e, "output", "") or str(e))
            if msg:
                raise click.ClickException(msg) from None
            raise click.ClickException(f"Build failed with exit code {e.returncode}.") from None
        except FileNotFoundError:
            raise click.ClickException("uv not found. Please install uv: pip install uv") from None

        if publish:
            try:
                import keyring

                log.info(f"Publishing stdlib-stubs module... {version}")
                publish_cmd = [
                    "uv",
                    "publish",
                    "-u",
                    "__token__",
                    "-p",
                    keyring.get_password("stubber", "uv_pipy_token"),
                ]
                result = subprocess.run(
                    publish_cmd,
                    cwd=dist_stdlib_path,
                    text=True,
                    capture_output=True,
                )
                if result.returncode != 0:
                    err = (result.stderr or result.stdout or "Publish failed").strip()
                    raise click.ClickException(err)
                log.info("Published successfully")
            except ImportError:
                raise click.ClickException("keyring package not found. Please install: pip install keyring") from None
            except Exception as e:
                raise click.ClickException(f"Publish failed: {str(e)}") from None

    log.info("stdlib-stubs command completed successfully")
