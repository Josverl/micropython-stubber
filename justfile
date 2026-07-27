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
docs:
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

# build standalone ports <stable> <unix>
sa_build v="stable" p="unix":
    uv run sa_ports_build.py --version {{v}} {{p}}

# stub standalone ports
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

# TODO
# Build stable and preview wasm binaries, using the 'pyscript'
wasm_build v="stable":
    # in all .pyi files
    # re.replace <JsProxy \d+> with <JsProxy nn>
    # re.replace -preview with ""
    # re.replace -233 with ""
    # re.replace 233 with ""
    # copy from temp folder to micropython-stubs/stubs 
    stubber merge --port webassembly --variant pyscript --version {{v}}
    stubber build --port webassembly --variant pyscript --version {{v}}
    
# wasm_build:
#     # uv run sa_ports_build.py --version stable webassembly --variant pyscript --fw-path webassembly-stubber/firmware/webassembly
#     uv run sa_ports_build.py --version preview webassembly --variant pyscript --fw-path webassembly-stubber/firmware/webassembly
