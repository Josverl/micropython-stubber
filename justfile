# https://just.systems

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
    uv sync --group dev --group test


# update the dependencies
update:
    uv lock --upgrade

# Build the project documentation
docs:
    @echo "Building documentation..."
    uv sync --group docs
    docs\make.bat html

# bump to the next patch level, including all .mpy files
next_patch:
    uvx bump-my-version bump patch
    @just variants
    uvx bump-my-version show current_version

variants:
    @echo "Building .mpy files..."
    uv run stubber make-variants
    uv run stubber make-variants --target ./mip/v5 --version 1.18
    uv run stubber make-variants --target ./mip/v6 --version 1.19.1

build:
    @echo "Building the project..."
    uv build

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