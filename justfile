# https://just.systems
# set allow-duplicate-variables 
set allow-duplicate-recipes

# import ?'repos/micropython-stubs/justfile'

# Set shell for Windows OSs:
set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# Run `[script]` recipes with uv so inline script metadata (dependencies) is honored
set script-interpreter := ['uv', 'run', '--script']

# keyring entry used to store/retrieve the pypi token for publishing
pypi_service := "pypi"
pypi_token_name := "micropython-stubber_publish"

default:
    @just --list

# init the development environment
init:
    @just sync
    uv run stubber clone --add-stubs
    uv run stubber switch stable

# sync with dev,test
sync:
    uv sync --group dev --group test

# update the dependencies
update:
    uv lock --upgrade

# Build the project documentation
sphinx:
    @echo "Building documentation..."
    uv sync --group docs
    docs\make.bat html

# bump to the next patch level, including all .mpy files
next_patch:
    uvx bump-my-version bump patch
    @just variants
    uvx bump-my-version show current_version

# create .mpy files for all variants
variants:
    @echo "Building .mpy files..."
    uv run stubber make-variants
    uv run stubber make-variants --target ./mip/v6 --version 1.19.1
    # uv run stubber make-variants --target ./mip/v5 --version 1.18
# Build MicroPython-stubber
build:
    @echo "Building the project..."
    uv build

# Build the stubs for a specific version of MicroPython (stable or preview)
build_stubs version="stable" *ARGS:
    uv run stubber build --version {{version}} {{ARGS}}


# -----------------------------------------------------------------------------------------------
# Release process
# The release recipe pushes an untagged version commit and dispatches .github/workflows/release.yml.
# CI tests that exact commit, creates a draft release with all assets, publishes to PyPI using
# trusted publishing (OIDC, no token), then publishes the immutable GitHub release.
# -----------------------------------------------------------------------------------------------

# bump the version and .mpy variants, then push the untagged commit for CI to test and release
# bump = major | minor | patch (default) | prerelease
[confirm("Bump the version and push a release commit for CI to test and publish? Continue?")]
[script]
release bump="patch":
    # /// script
    # requires-python = ">=3.9"
    # ///
    import subprocess

    def run(*args):
        subprocess.run(args, check=True)

    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if branch != "main":
        raise SystemExit(f"Releases must be run from main, not {branch or 'detached HEAD'}")

    run("uvx", "bump-my-version", "bump", "{{ bump }}")

    version = subprocess.run(
        ["uvx", "bump-my-version", "show", "current_version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    run("just", "variants")
    run("git", "add", "-A")
    run("git", "commit", "-m", f"Release v{version}")

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    run("git", "push", "origin", branch)
    run(
        "gh", "workflow", "run", "release.yml",
        "--ref", branch,
        "--field", f"version={version}",
        "--field", f"commit={commit}",
    )


# publish the micropython-stubber package to pypi, using a token stored in the system keyring
[script]
publish: build
    # /// script
    # requires-python = ">=3.9"
    # dependencies = ["keyring"]
    # ///
    import keyring
    import subprocess
    import sys

    print("Publishing micropython-stubber to pypi")
    token = keyring.get_password("{{ pypi_service }}", "{{ pypi_token_name }}")
    if not token:
        sys.exit("No pypi token found in keyring")

    subprocess.run(
        ["uv", "publish", "--token", token],
        check=True,
    )

# store the pypi token used by the `publish` recipe in the system keyring
[script]
store_token:
    # /// script
    # requires-python = ">=3.9"
    # dependencies = ["keyring"]
    # ///
    import getpass
    import keyring

    token = getpass.getpass("Enter the pypi token: ").strip()
    if not token:
        raise SystemExit("No token provided")

    keyring.set_password("{{ pypi_service }}", "{{ pypi_token_name }}", token)
    print("Stored pypi token in keyring ({{ pypi_service }} / {{ pypi_token_name }})")

# Build and register the Unix and Windows standalone interpreters.
sa_build v="stable" :
    uv run sa_ports_build.py --version {{v}} unix
    uv run sa_ports_build.py --version {{v}} windows


# Build the WebAssembly PyScript interpreter bundle.
sa_wasm v="stable" :
    uv run sa_ports_build.py --version {{v}} webassembly --variant pyscript

# Generate, merge, and package Unix or Windows standalone stubs.
sa_stub v="stable" p="unix":
    uv run sa_ports_stub.py --stubs-root ./repos/micropython-stubs --version {{v}} {{p}}


# Prepare for wasm (manual stub) 
[working-directory: 'webassembly-stubber']
wasm_stub:
    # make a temp folder
    mkdir -p WASM-TEMP
    echo "*" > WASM-TEMP/.gitignore
    # start webserver and browser
    uv run serve.py

# copy from temp folder to micropython-stubs/stubs 
wasm_copy: wasm_cleanup
    cp -r webassembly-stubber/WASM-TEMP/micropython-* repos/micropython-stubs/stubs


[script]
wasm_cleanup path="webassembly-stubber/WASM-TEMP/micropython-v1_28_0-webassembly-pyscript":
    # /// script
    # requires-python = ">=3.9"
    # ///
    from pathlib import Path
    import re

    root = Path(r"{{path}}")
    if not root.is_dir():
        raise SystemExit(f"Stub directory does not exist: {root}")

    replacements = (
        (re.compile(r"<JsProxy \d+>"), "<JsProxy nn>"),
        (re.compile(r"-preview"), ""),
        (re.compile(r"-233"), ""),
        (re.compile(r"233"), ""),
    )
    counts = [0] * len(replacements)
    changed_files = 0
    removed_zone_files = 0

    for zone_path in sorted(root.rglob("*.*:Zone.Identifier")):
        if zone_path.is_file():
            zone_path.unlink()
            removed_zone_files += 1

    for stub_path in sorted(root.rglob("*.pyi")):
        original = stub_path.read_text(encoding="utf-8")
        cleaned = original
        for index, (pattern, replacement) in enumerate(replacements):
            cleaned, count = pattern.subn(replacement, cleaned)
            counts[index] += count

        if cleaned != original:
            stub_path.write_text(cleaned, encoding="utf-8")
            changed_files += 1

    print(f"Cleaned {changed_files} .pyi file(s) in {root}")
    print(f"Removed {removed_zone_files} Zone.Identifier file(s)")
    print(f"Replacement counts: JsProxy={counts[0]}, -preview={counts[1]}, -233={counts[2]}, 233={counts[3]}")



# Merge and package generated WebAssembly PyScript stubs.
wasm_build v="stable":
    stubber merge --port webassembly --board auto --version {{v}}
    stubber build --port webassembly --board auto --version {{v}}
    
# wasm_build:
#     # uv run sa_ports_build.py --version stable webassembly --variant pyscript --fw-path webassembly-stubber/firmware/webassembly
#     uv run sa_ports_build.py --version preview webassembly --variant pyscript --fw-path webassembly-stubber/firmware/webassembly


stdlib:
    python repos/micropython-stubs/publish/micropython-stdlib-stubs/build.py